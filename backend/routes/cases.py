import json
from flask import Blueprint, request, jsonify, session
from backend.auth import login_required
from backend.db import get_db_cursor, query_one, query_all

cases_bp = Blueprint("cases", __name__, url_prefix="/api/cases")

ALLOWED_CASE_SORTS = {
    "case_created_at": "case_created_at",
    "risk_score": "risk_score",
    "amount": "amount",
    "priority": "priority"
}

@cases_bp.route("", methods=["GET"])
@login_required
def get_cases():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(100, max(1, int(request.args.get("limit", 20))))
    offset = (page - 1) * limit

    sort_by = request.args.get("sort_by", "case_created_at")
    sort_dir = request.args.get("sort_dir", "desc").upper()
    if sort_dir not in ("ASC", "DESC"):
        sort_dir = "DESC"
    order_col = ALLOWED_CASE_SORTS.get(sort_by, "case_created_at")

    conditions = []
    params = []

    case_status = request.args.get("status")
    if case_status in ("open", "investigating", "resolved_fraud", "resolved_legitimate"):
        conditions.append("case_status = %s")
        params.append(case_status)

    priority = request.args.get("priority")
    if priority in ("low", "medium", "high", "critical"):
        conditions.append("priority = %s")
        params.append(priority)

    assigned_to = request.args.get("assigned_to")
    if assigned_to:
        if assigned_to == "unassigned":
            conditions.append("assigned_to IS NULL")
        else:
            try:
                conditions.append("assigned_to = %s")
                params.append(int(assigned_to))
            except ValueError:
                pass

    search = request.args.get("search", "").strip()
    if search:
        conditions.append("(transaction_reference LIKE %s OR customer_name LIKE %s OR merchant_name LIKE %s)")
        like_term = f"%{search}%"
        params.extend([like_term, like_term, like_term])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Count query
    count_sql = f"SELECT COUNT(*) AS total FROM v_case_overview {where_clause}"
    total_row = query_one(count_sql, tuple(params))
    total_count = total_row["total"] if total_row else 0

    # Data query
    data_sql = f"""
        SELECT *
        FROM v_case_overview
        {where_clause}
        ORDER BY {order_col} {sort_dir}
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

@cases_bp.route("/<int:case_id>", methods=["GET"])
@login_required
def get_case(case_id):
    case = query_one("SELECT * FROM v_case_overview WHERE case_id = %s", (case_id,))
    if not case:
        return jsonify({"error": "Investigation case not found.", "code": "NOT_FOUND"}), 404

    # Fetch triggered risk factors
    factors = query_all("""
        SELECT rf.id, rf.rule_code, rf.rule_name, rf.points, rf.explanation
        FROM risk_factors rf
        JOIN risk_assessments ra ON rf.assessment_id = ra.id
        WHERE ra.transaction_id = %s
        ORDER BY rf.points DESC
    """, (case["transaction_id"],))

    # Fetch investigation notes
    notes = query_all("""
        SELECT n.id, n.note_text, n.created_at, u.id AS author_id, u.full_name AS author_name, u.role AS author_role
        FROM investigation_notes n
        JOIN users u ON n.user_id = u.id
        WHERE n.case_id = %s
        ORDER BY n.created_at ASC
    """, (case_id,))

    # Fetch case audit history
    audit_history = query_all("""
        SELECT a.id, a.action, a.details, a.created_at, u.full_name AS actor_name
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.entity_type = 'investigation_cases' AND a.entity_id = %s
        ORDER BY a.created_at DESC
    """, (case_id,))

    case["factors"] = factors
    case["notes"] = notes
    case["audit_history"] = audit_history

    return jsonify({"case": case})

@cases_bp.route("/<int:case_id>", methods=["PATCH"])
@login_required
def update_case(case_id):
    data = request.get_json(silent=True) or {}
    user_id = session.get("user_id")

    existing = query_one("SELECT id, case_status, priority, assigned_to FROM investigation_cases WHERE id = %s", (case_id,))
    if not existing:
        return jsonify({"error": "Case not found.", "code": "NOT_FOUND"}), 404

    new_status = data.get("case_status")
    resolution_notes = data.get("resolution_notes")
    new_priority = data.get("priority")
    new_assigned_to = data.get("assigned_to")

    with get_db_cursor(commit=True, dictionary=True) as cursor:
        # If updating status, execute the atomic stored procedure sp_update_case_status
        if new_status and new_status != existing["case_status"]:
            try:
                cursor.callproc("sp_update_case_status", (case_id, user_id, new_status, resolution_notes or ""))
            except Exception as e:
                return jsonify({"error": str(e), "code": "PROCEDURE_ERROR"}), 400

        # Update assignment if provided
        if "assigned_to" in data and new_assigned_to != existing["assigned_to"]:
            cursor.execute("""
                UPDATE investigation_cases
                SET assigned_to = %s, updated_at = NOW()
                WHERE id = %s
            """, (new_assigned_to, case_id))

            cursor.execute("""
                INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
                VALUES (%s, 'CASE_ASSIGNMENT_UPDATED', 'investigation_cases', %s, %s, NOW())
            """, (user_id, case_id, json.dumps({
                "old_assigned_to": existing["assigned_to"],
                "new_assigned_to": new_assigned_to
            })))

        # Update priority if provided
        if new_priority and new_priority in ("low", "medium", "high", "critical") and new_priority != existing["priority"]:
            cursor.execute("""
                UPDATE investigation_cases
                SET priority = %s, updated_at = NOW()
                WHERE id = %s
            """, (new_priority, case_id))

            cursor.execute("""
                INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
                VALUES (%s, 'CASE_PRIORITY_UPDATED', 'investigation_cases', %s, %s, NOW())
            """, (user_id, case_id, json.dumps({
                "old_priority": existing["priority"],
                "new_priority": new_priority
            })))

    # Return updated case overview
    updated = query_one("SELECT * FROM v_case_overview WHERE case_id = %s", (case_id,))
    return jsonify({
        "message": "Case updated successfully",
        "case": updated
    })

@cases_bp.route("/<int:case_id>/notes", methods=["POST"])
@login_required
def add_case_note(case_id):
    data = request.get_json(silent=True) or {}
    note_text = (data.get("note_text") or "").strip()

    if not note_text:
        return jsonify({"error": "Note text cannot be empty.", "code": "VALIDATION_ERROR"}), 400

    user_id = session.get("user_id")

    existing = query_one("SELECT id FROM investigation_cases WHERE id = %s", (case_id,))
    if not existing:
        return jsonify({"error": "Case not found.", "code": "NOT_FOUND"}), 404

    with get_db_cursor(commit=True, dictionary=True) as cursor:
        cursor.execute("""
            INSERT INTO investigation_notes (case_id, user_id, note_text, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (case_id, user_id, note_text))
        note_id = cursor.lastrowid

        cursor.execute("""
            UPDATE investigation_cases SET updated_at = NOW() WHERE id = %s
        """, (case_id,))

        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
            VALUES (%s, 'CASE_NOTE_ADDED', 'investigation_cases', %s, %s, NOW())
        """, (user_id, case_id, json.dumps({"note_id": note_id})))

    note = query_one("""
        SELECT n.id, n.note_text, n.created_at, u.id AS author_id, u.full_name AS author_name, u.role AS author_role
        FROM investigation_notes n
        JOIN users u ON n.user_id = u.id
        WHERE n.id = %s
    """, (note_id,))

    return jsonify({
        "message": "Note added successfully",
        "note": note
    }), 201
