from flask import Blueprint, request, jsonify
from backend.auth import login_required, admin_required
from backend.db import query_all, query_one

admin_bp = Blueprint("admin", __name__, url_prefix="/api")

@admin_bp.route("/admin/audit-logs", methods=["GET"])
@login_required
def get_audit_logs():
    page = max(1, int(request.args.get("page", 1)))
    limit = min(100, max(1, int(request.args.get("limit", 25))))
    offset = (page - 1) * limit

    conditions = []
    params = []

    action = request.args.get("action")
    if action:
        conditions.append("a.action = %s")
        params.append(action)

    entity_type = request.args.get("entity_type")
    if entity_type:
        conditions.append("a.entity_type = %s")
        params.append(entity_type)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    count_sql = f"SELECT COUNT(*) AS total FROM audit_logs a {where_clause}"
    total_row = query_one(count_sql, tuple(params))
    total_count = total_row["total"] if total_row else 0

    data_sql = f"""
        SELECT 
            a.id, a.user_id, a.action, a.entity_type, a.entity_id, a.details, a.created_at,
            u.full_name AS user_name, u.email AS user_email, u.role AS user_role
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.id
        {where_clause}
        ORDER BY a.created_at DESC
        LIMIT %s OFFSET %s
    """
    items = query_all(data_sql, tuple(params + [limit, offset]))

    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1

    return jsonify({
        "items": items,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    })

@admin_bp.route("/users", methods=["GET"])
@login_required
def get_users_list():
    """Returns investigators and admins for assignment select dropdowns."""
    users = query_all("""
        SELECT id, full_name, email, role, is_active
        FROM users
        WHERE is_active = TRUE
        ORDER BY full_name ASC
    """)
    return jsonify({"users": users})

@admin_bp.route("/customers", methods=["GET"])
@login_required
def get_customers_list():
    customers = query_all("""
        SELECT id, customer_reference, full_name, email
        FROM customers
        ORDER BY full_name ASC
    """)
    return jsonify({"customers": customers})

@admin_bp.route("/merchants", methods=["GET"])
@login_required
def get_merchants_list():
    merchants = query_all("""
        SELECT id, merchant_reference, merchant_name, category
        FROM merchants
        ORDER BY merchant_name ASC
    """)
    return jsonify({"merchants": merchants})
