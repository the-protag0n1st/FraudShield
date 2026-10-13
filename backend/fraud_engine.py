import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

RULES_VERSION = "v1.0"

# Default scoring parameters
DEFAULT_CONFIG = {
    "amount_threshold": Decimal("5000.00"),
    "velocity_count": 3,              # 3+ other txns in last 10 minutes
    "amount_multiplier": Decimal("3.0"),  # 3x historical average
    "min_history_count": 3,           # Min prior txns needed for spike & merchant rules
    "failed_attempts_threshold": 2,   # 2+ declined txns in last 30 minutes
    "velocity_window_minutes": 10,
    "failed_window_minutes": 30,
    "location_window_minutes": 60,
    "flag_case_threshold": 60         # High and Critical scores create investigation cases
}

def determine_risk_level(score: int) -> str:
    """Translates numerical risk score (0-100) into categorical tier."""
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 30:
        return "medium"
    return "low"

def evaluate_rules(txn: Dict[str, Any], history: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Pure deterministic fraud scoring engine.
    Computes risk score and explanations with zero database side-effects.
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    amount = Decimal(str(txn.get("amount", 0)))
    factors: List[Dict[str, Any]] = []
    total_points = 0

    # Rule A: High Transaction Amount
    threshold = cfg["amount_threshold"]
    if amount >= threshold:
        pts = 25
        total_points += pts
        factors.append({
            "rule_code": "RULE_A_HIGH_AMOUNT",
            "rule_name": "High Transaction Amount",
            "points": pts,
            "explanation": f"Transaction amount (${amount:,.2f}) meets or exceeds high-value threshold (${threshold:,.2f})."
        })

    # Rule B: Transaction Velocity Burst (e.g. >= 3 txns in last 10 mins)
    recent_10m_count = history.get("recent_10m_count", 0)
    if recent_10m_count >= cfg["velocity_count"]:
        pts = 20
        total_points += pts
        factors.append({
            "rule_code": "RULE_B_HIGH_VELOCITY",
            "rule_name": "Rapid Transaction Velocity",
            "points": pts,
            "explanation": f"Customer performed {recent_10m_count} other transactions in the preceding {cfg['velocity_window_minutes']} minutes (threshold: {cfg['velocity_count']})."
        })

    # Rule C: Unusually Large Transaction Spike vs Historical Average
    prior_count = history.get("prior_count", 0)
    prior_avg = Decimal(str(history.get("prior_avg_amount", 0) or 0))
    if prior_count >= cfg["min_history_count"] and prior_avg > Decimal("0"):
        multiple = amount / prior_avg
        if multiple >= cfg["amount_multiplier"]:
            pts = 20
            total_points += pts
            factors.append({
                "rule_code": "RULE_C_AMOUNT_SPIKE",
                "rule_name": "Unusual Amount Relative to History",
                "points": pts,
                "explanation": f"Transaction amount (${amount:,.2f}) is {float(multiple):.1f}x the customer's historical average (${prior_avg:,.2f}) across {prior_count} prior transactions."
            })

    # Rule D: Failed Attempt Pattern
    recent_failed_count = history.get("recent_failed_count", 0)
    if recent_failed_count >= cfg["failed_attempts_threshold"]:
        pts = 15
        total_points += pts
        factors.append({
            "rule_code": "RULE_D_FAILED_ATTEMPTS",
            "rule_name": "Prior Failed Transaction Attempts",
            "points": pts,
            "explanation": f"Customer recorded {recent_failed_count} declined transaction attempts in the preceding {cfg['failed_window_minutes']} minutes."
        })

    # Rule E: Unusual / Novel Merchant
    prior_merchant_count = history.get("prior_with_this_merchant", 0)
    if prior_count >= cfg["min_history_count"] and prior_merchant_count == 0:
        pts = 10
        total_points += pts
        merchant_name = txn.get("merchant_name") or f"Merchant #{txn.get('merchant_id')}"
        factors.append({
            "rule_code": "RULE_E_NEW_MERCHANT",
            "rule_name": "First-Time Merchant Interaction",
            "points": pts,
            "explanation": f"First recorded transaction with '{merchant_name}' for an established customer profile ({prior_count} prior transactions)."
        })

    # Rule F: Inconsistent Geographic Location
    last_country = history.get("last_recent_country")
    current_country = txn.get("country_code", "US")
    if last_country and last_country != current_country:
        pts = 20
        total_points += pts
        factors.append({
            "rule_code": "RULE_F_LOCATION_MISMATCH",
            "rule_name": "Inconsistent Geographic Location",
            "points": pts,
            "explanation": f"Transaction originated from '{current_country}' shortly after previous activity from '{last_country}' within {cfg['location_window_minutes']} minutes."
        })

    final_score = min(100, total_points)
    risk_level = determine_risk_level(final_score)

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "rules_version": RULES_VERSION,
        "factors": factors,
        "is_flagged": final_score >= cfg["flag_case_threshold"]
    }

def fetch_transaction_history(cursor, customer_id: int, merchant_id: int, current_txn_id: int, current_timestamp: datetime) -> Dict[str, Any]:
    """
    Executes efficient aggregated queries using composite indexes to collect
    historical context for the pure scoring engine. Excludes the current transaction.
    """
    # 1. Lifetime customer aggregates: prior count, avg amount, count with this merchant
    sql_general = """
        SELECT 
            COUNT(*) AS prior_count,
            COALESCE(AVG(amount), 0.00) AS prior_avg_amount,
            COUNT(CASE WHEN merchant_id = %s THEN 1 END) AS prior_with_this_merchant
        FROM transactions
        WHERE customer_id = %s
          AND id != %s
          AND transaction_timestamp <= %s
    """
    cursor.execute(sql_general, (merchant_id, customer_id, current_txn_id, current_timestamp))
    general_stats = cursor.fetchone() or {"prior_count": 0, "prior_avg_amount": 0.00, "prior_with_this_merchant": 0}

    # 2. Velocity: transactions in the 10 minutes prior
    sql_velocity = """
        SELECT COUNT(*) AS recent_10m_count
        FROM transactions
        WHERE customer_id = %s
          AND id != %s
          AND transaction_timestamp BETWEEN (%s - INTERVAL 10 MINUTE) AND %s
    """
    cursor.execute(sql_velocity, (customer_id, current_txn_id, current_timestamp, current_timestamp))
    vel_stats = cursor.fetchone() or {"recent_10m_count": 0}

    # 3. Failed attempts: declined transactions in the 30 minutes prior
    sql_failed = """
        SELECT COUNT(*) AS recent_failed_count
        FROM transactions
        WHERE customer_id = %s
          AND id != %s
          AND transaction_status = 'declined'
          AND transaction_timestamp BETWEEN (%s - INTERVAL 30 MINUTE) AND %s
    """
    cursor.execute(sql_failed, (customer_id, current_txn_id, current_timestamp, current_timestamp))
    failed_stats = cursor.fetchone() or {"recent_failed_count": 0}

    # 4. Location consistency: last transaction's country code within the last 60 minutes
    sql_loc = """
        SELECT country_code
        FROM transactions
        WHERE customer_id = %s
          AND id != %s
          AND transaction_timestamp BETWEEN (%s - INTERVAL 60 MINUTE) AND %s
        ORDER BY transaction_timestamp DESC
        LIMIT 1
    """
    cursor.execute(sql_loc, (customer_id, current_txn_id, current_timestamp, current_timestamp))
    loc_row = cursor.fetchone()
    last_recent_country = loc_row["country_code"] if loc_row else None

    return {
        "prior_count": general_stats["prior_count"],
        "prior_avg_amount": general_stats["prior_avg_amount"],
        "prior_with_this_merchant": general_stats["prior_with_this_merchant"],
        "recent_10m_count": vel_stats["recent_10m_count"],
        "recent_failed_count": failed_stats["recent_failed_count"],
        "last_recent_country": last_recent_country
    }

def score_and_persist_assessment(cursor, transaction_id: int, user_id: int = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Atomic evaluation and persistence:
    1. Locks and reads transaction record.
    2. Gathers historical data.
    3. Runs deterministic rule evaluation.
    4. Upserts risk_assessment (ON DUPLICATE KEY UPDATE) and replaces risk_factors.
    5. Creates or updates investigation_case if score >= 60.
    6. Logs audit event.
    Must be called inside an active transaction.
    """
    # Lock transaction row
    cursor.execute("""
        SELECT t.*, m.merchant_name, c.full_name AS customer_name
        FROM transactions t
        JOIN merchants m ON t.merchant_id = m.id
        JOIN customers c ON t.customer_id = c.id
        WHERE t.id = %s
        FOR UPDATE
    """, (transaction_id,))
    txn = cursor.fetchone()
    if not txn:
        raise ValueError(f"Transaction with ID {transaction_id} not found.")

    # Load history
    history = fetch_transaction_history(
        cursor=cursor,
        customer_id=txn["customer_id"],
        merchant_id=txn["merchant_id"],
        current_txn_id=txn["id"],
        current_timestamp=txn["transaction_timestamp"]
    )

    # Evaluate
    result = evaluate_rules(txn, history, config)
    score = result["risk_score"]
    level = result["risk_level"]
    factors = result["factors"]

    # Upsert risk_assessment
    cursor.execute("""
        INSERT INTO risk_assessments (transaction_id, risk_score, risk_level, rules_version, assessed_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            risk_score = VALUES(risk_score),
            risk_level = VALUES(risk_level),
            rules_version = VALUES(rules_version),
            assessed_at = NOW()
    """, (transaction_id, score, level, RULES_VERSION))

    # Retrieve assessment ID
    cursor.execute("SELECT id FROM risk_assessments WHERE transaction_id = %s", (transaction_id,))
    assess_row = cursor.fetchone()
    assessment_id = assess_row["id"]

    # Replace risk factors atomically
    cursor.execute("DELETE FROM risk_factors WHERE assessment_id = %s", (assessment_id,))
    for factor in factors:
        cursor.execute("""
            INSERT INTO risk_factors (assessment_id, rule_code, rule_name, points, explanation)
            VALUES (%s, %s, %s, %s, %s)
        """, (assessment_id, factor["rule_code"], factor["rule_name"], factor["points"], factor["explanation"]))

    # Handle Investigation Case creation/update if flagged
    case_created = False
    case_id = None
    if result["is_flagged"]:
        priority = "critical" if level == "critical" else "high"
        cursor.execute("""
            INSERT INTO investigation_cases (transaction_id, case_status, priority, created_at, updated_at)
            VALUES (%s, 'open', %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                priority = VALUES(priority),
                updated_at = NOW()
        """, (transaction_id, priority))
        
        cursor.execute("SELECT id, case_status FROM investigation_cases WHERE transaction_id = %s", (transaction_id,))
        case_row = cursor.fetchone()
        case_id = case_row["id"]
        case_created = True

    # Audit log entry for assessment
    import json
    cursor.execute("""
        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
        VALUES (%s, 'TRANSACTION_ASSESSED', 'transactions', %s, %s, NOW())
    """, (
        user_id,
        transaction_id,
        json.dumps({
            "score": score,
            "level": level,
            "factor_count": len(factors),
            "case_id": case_id
        })
    ))

    return {
        "transaction_id": transaction_id,
        "assessment_id": assessment_id,
        "risk_score": score,
        "risk_level": level,
        "rules_version": RULES_VERSION,
        "factors": factors,
        "case_id": case_id,
        "is_flagged": result["is_flagged"]
    }
