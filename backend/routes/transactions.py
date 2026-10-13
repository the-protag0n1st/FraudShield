import time
import random
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Blueprint, request, jsonify, session
from backend.auth import login_required
from backend.db import get_db_cursor, query_one, query_all
from backend.fraud_engine import score_and_persist_assessment

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")

ALLOWED_SORT_FIELDS = {
    "transaction_timestamp": "t.transaction_timestamp",
    "amount": "t.amount",
    "risk_score": "r.risk_score",
    "created_at": "t.created_at"
}

@transactions_bp.route("", methods=["GET"])
@login_required
def get_transactions():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(100, max(1, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit

    sort_by = request.args.get("sort_by", "transaction_timestamp")
    sort_dir = request.args.get("sort_dir", "desc").upper()
    if sort_dir not in ("ASC", "DESC"):
        sort_dir = "DESC"
    order_column = ALLOWED_SORT_FIELDS.get(sort_by, "t.transaction_timestamp")

    # Dynamic filter conditions with parameterized values
    conditions = []
    params = []

    search = request.args.get("search", "").strip()
    if search:
        conditions.append("(t.transaction_reference LIKE %s OR c.full_name LIKE %s OR m.merchant_name LIKE %s)")
        like_term = f"%{search}%"
        params.extend([like_term, like_term, like_term])

    risk_level = request.args.get("risk_level")
    if risk_level in ("low", "medium", "high", "critical"):
        conditions.append("r.risk_level = %s")
        params.append(risk_level)

    status = request.args.get("status")
    if status in ("approved", "declined", "pending"):
        conditions.append("t.transaction_status = %s")
        params.append(status)

    min_amount = request.args.get("min_amount")
    if min_amount:
        try:
            conditions.append("t.amount >= %s")
            params.append(float(min_amount))
        except ValueError:
            pass

    max_amount = request.args.get("max_amount")
    if max_amount:
        try:
            conditions.append("t.amount <= %s")
            params.append(float(max_amount))
        except ValueError:
            pass

    from_date = request.args.get("from_date")
    if from_date:
        conditions.append("t.transaction_timestamp >= %s")
        params.append(from_date)

    to_date = request.args.get("to_date")
    if to_date:
        conditions.append("t.transaction_timestamp <= %s")
        params.append(to_date)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Count query
    count_sql = f"""
        SELECT COUNT(t.id) AS total
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        JOIN merchants m ON t.merchant_id = m.id
        LEFT JOIN risk_assessments r ON t.id = r.transaction_id
        {where_clause}
    """
    total_row = query_one(count_sql, tuple(params))
    total_count = total_row["total"] if total_row else 0

    # Data query
    data_sql = f"""
        SELECT 
            t.id, t.transaction_reference, t.amount, t.currency,
            t.transaction_type, t.transaction_status, t.transaction_timestamp,
            t.channel, t.location, t.country_code,
            c.id AS customer_id, c.customer_reference, c.full_name AS customer_name,
            m.id AS merchant_id, m.merchant_reference, m.merchant_name, m.category AS merchant_category,
            r.risk_score, r.risk_level,
            ic.id AS case_id, ic.case_status, ic.priority AS case_priority
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        JOIN merchants m ON t.merchant_id = m.id
        LEFT JOIN risk_assessments r ON t.id = r.transaction_id
        LEFT JOIN investigation_cases ic ON t.id = ic.transaction_id
        {where_clause}
        ORDER BY {order_column} {sort_dir}
        LIMIT %s OFFSET %s
    """
    data_params = params + [limit, offset]
    items = query_all(data_sql, tuple(data_params))

    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1

    return jsonify({
        "items": items,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    })

@transactions_bp.route("/<int:txn_id>", methods=["GET"])
@login_required
def get_transaction(txn_id):
    sql = """
        SELECT 
            t.*,
            c.customer_reference, c.full_name AS customer_name, c.email AS customer_email, c.phone AS customer_phone,
            m.merchant_reference, m.merchant_name, m.category AS merchant_category, m.location AS merchant_location,
            r.id AS assessment_id, r.risk_score, r.risk_level, r.rules_version, r.assessed_at,
            ic.id AS case_id, ic.case_status, ic.priority AS case_priority, ic.assigned_to, ic.resolved_at
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        JOIN merchants m ON t.merchant_id = m.id
        LEFT JOIN risk_assessments r ON t.id = r.transaction_id
        LEFT JOIN investigation_cases ic ON t.id = ic.transaction_id
        WHERE t.id = %s
    """
    txn = query_one(sql, (txn_id,))
    if not txn:
        return jsonify({"error": "Transaction not found", "code": "NOT_FOUND"}), 404

    factors = []
    if txn.get("assessment_id"):
        factors = query_all("""
            SELECT id, rule_code, rule_name, points, explanation
            FROM risk_factors
            WHERE assessment_id = %s
            ORDER BY points DESC
        """, (txn["assessment_id"],))

    txn["factors"] = factors
    return jsonify({"transaction": txn})

@transactions_bp.route("", methods=["POST"])
@login_required
def create_transaction():
    data = request.get_json(silent=True) or {}
    
    # Validation
    customer_id = data.get("customer_id")
    merchant_id = data.get("merchant_id")
    amount = data.get("amount")

    if not customer_id or not merchant_id or amount is None:
        return jsonify({"error": "customer_id, merchant_id, and amount are required.", "code": "VALIDATION_ERROR"}), 400

    try:
        amount_dec = Decimal(str(amount))
        if amount_dec <= Decimal("0"):
            return jsonify({"error": "Amount must be strictly greater than 0.", "code": "VALIDATION_ERROR"}), 400
    except Exception:
        return jsonify({"error": "Invalid decimal amount.", "code": "VALIDATION_ERROR"}), 400

    currency = (data.get("currency") or "USD").upper()[:3]
    txn_type = data.get("transaction_type") or "purchase"
    txn_status = data.get("transaction_status") or "approved"
    channel = data.get("channel") or "online"
    location = data.get("location") or "New York, USA"
    country_code = (data.get("country_code") or "US").upper()[:2]
    
    timestamp_str = data.get("transaction_timestamp")
    if timestamp_str:
        try:
            txn_timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            txn_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        txn_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate unique reference
    unique_ref = f"TXN-{int(time.time())}-{random.randint(1000, 9999)}"

    user_id = session.get("user_id")

    # Atomic write of transaction and risk scoring
    with get_db_cursor(commit=True, dictionary=True) as cursor:
        cursor.execute("""
            INSERT INTO transactions (
                transaction_reference, customer_id, merchant_id, amount, currency,
                transaction_type, transaction_status, transaction_timestamp, channel,
                location, country_code, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            unique_ref, customer_id, merchant_id, amount_dec, currency,
            txn_type, txn_status, txn_timestamp, channel,
            location, country_code
        ))
        txn_id = cursor.lastrowid

        # Evaluate and persist assessment immediately
        assessment_res = score_and_persist_assessment(
            cursor=cursor,
            transaction_id=txn_id,
            user_id=user_id
        )

    return jsonify({
        "message": "Transaction created and assessed successfully",
        "transaction_id": txn_id,
        "transaction_reference": unique_ref,
        "assessment": assessment_res
    }), 201

@transactions_bp.route("/<int:txn_id>/assess", methods=["POST"])
@login_required
def reassess_transaction(txn_id):
    user_id = session.get("user_id")
    with get_db_cursor(commit=True, dictionary=True) as cursor:
        assessment_res = score_and_persist_assessment(
            cursor=cursor,
            transaction_id=txn_id,
            user_id=user_id
        )
    return jsonify({
        "message": "Transaction reassessed successfully",
        "assessment": assessment_res
    })

@transactions_bp.route("/demo/scenario", methods=["POST"])
@login_required
def trigger_demo_scenario():
    """
    Generates controlled deterministic demo scenarios on the fly for live evaluation presentations.
    """
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "high_amount")

    now = datetime.now()
    user_id = session.get("user_id")

    # Fetch reference customer and merchants
    customer = query_one("SELECT id, full_name FROM customers ORDER BY id LIMIT 1")
    merchants = query_all("SELECT id, merchant_name, category FROM merchants ORDER BY id LIMIT 5")

    if not customer or not merchants:
        return jsonify({"error": "No customers or merchants found in database. Run seed first.", "code": "SEED_MISSING"}), 400

    cid = customer["id"]
    m1 = merchants[0] # ElectroDepot
    m_luxury = merchants[2] if len(merchants) > 2 else merchants[0]
    m_crypto = merchants[4] if len(merchants) > 4 else merchants[0]

    with get_db_cursor(commit=True, dictionary=True) as cursor:
        if scenario == "normal":
            # Normal low-risk purchase
            ref = f"DEMO-NORM-{int(time.time())}"
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp, channel,
                    location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', NOW(), 'pos', 'New York, USA', 'US', NOW())
            """, (ref, cid, m1["id"], Decimal("45.50")))
            target_id = cursor.lastrowid
            result = score_and_persist_assessment(cursor, target_id, user_id=user_id)

        elif scenario == "high_amount":
            # Amount exceeds $5000 (Rule A +25 points)
            ref = f"DEMO-HIGHVAL-{int(time.time())}"
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp, channel,
                    location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', NOW(), 'online', 'Geneva, Switzerland', 'US', NOW())
            """, (ref, cid, m_luxury["id"], Decimal("7850.00")))
            target_id = cursor.lastrowid
            result = score_and_persist_assessment(cursor, target_id, user_id=user_id)

        elif scenario == "velocity_burst":
            # 4 rapid transactions within 3 minutes
            burst_time = now
            for i in range(3):
                cursor.execute("""
                    INSERT INTO transactions (
                        transaction_reference, customer_id, merchant_id, amount, currency,
                        transaction_type, transaction_status, transaction_timestamp, channel,
                        location, country_code, created_at
                    ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', %s, 'online', 'New York, USA', 'US', NOW())
                """, (f"DEMO-BURST-PRE-{i}-{int(time.time())}", cid, m1["id"], Decimal("120.00"), burst_time - timedelta(minutes=5 - i)))

            ref = f"DEMO-BURST-HIT-{int(time.time())}"
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp, channel,
                    location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', %s, 'online', 'New York, USA', 'US', NOW())
            """, (ref, cid, m1["id"], Decimal("450.00"), burst_time))
            target_id = cursor.lastrowid
            result = score_and_persist_assessment(cursor, target_id, user_id=user_id)

        elif scenario == "location_mismatch":
            # Activity in US 20 mins ago, then suddenly Singapore
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp, channel,
                    location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', %s, 'pos', 'New York, USA', 'US', NOW())
            """, (f"DEMO-LOC-PRE-{int(time.time())}", cid, m1["id"], Decimal("30.00"), now - timedelta(minutes=25)))

            ref = f"DEMO-LOC-JUMP-{int(time.time())}"
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp, channel,
                    location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', %s, 'online', 'Singapore, Singapore', 'SG', NOW())
            """, (ref, cid, m_crypto["id"], Decimal("1500.00"), now))
            target_id = cursor.lastrowid
            result = score_and_persist_assessment(cursor, target_id, user_id=user_id)

        elif scenario == "critical_combo":
            # Multi-vector fraud: Location mismatch + High amount + Spike + Failed attempt pattern (Critical 85+ score)
            # 2 declined attempts in last 15 minutes
            for i in range(2):
                cursor.execute("""
                    INSERT INTO transactions (
                        transaction_reference, customer_id, merchant_id, amount, currency,
                        transaction_type, transaction_status, transaction_timestamp, channel,
                        location, country_code, created_at
                    ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'declined', %s, 'online', 'New York, USA', 'US', NOW())
                """, (f"DEMO-CRIT-FAIL-{i}-{int(time.time())}", cid, m1["id"], Decimal("200.00"), now - timedelta(minutes=15 - i * 3)))

            # Immediate $8,900 transaction from Lagos, Nigeria
            ref = f"DEMO-CRIT-COMBO-{int(time.time())}"
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp, channel,
                    location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', 'purchase', 'approved', %s, 'online', 'Lagos, Nigeria', 'NG', NOW())
            """, (ref, cid, m_crypto["id"], Decimal("8950.00"), now))
            target_id = cursor.lastrowid
            result = score_and_persist_assessment(cursor, target_id, user_id=user_id)

        else:
            return jsonify({"error": f"Unknown scenario: {scenario}", "code": "INVALID_SCENARIO"}), 400

    return jsonify({
        "message": f"Scenario '{scenario}' executed successfully",
        "transaction_id": target_id,
        "transaction_reference": ref,
        "assessment": result
    }), 201
