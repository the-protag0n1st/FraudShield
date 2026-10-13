from flask import Blueprint, jsonify
from backend.auth import login_required
from backend.db import query_one, query_all

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("/summary", methods=["GET"])
@login_required
def get_summary():
    # 1. Fetch aggregate metrics from database view v_dashboard_summary
    kpi = query_one("SELECT * FROM v_dashboard_summary") or {}
    
    # 2. Fetch recent high/critical flagged transactions
    recent_flagged = query_all("""
        SELECT 
            t.id, t.transaction_reference, t.amount, t.currency,
            t.transaction_timestamp, t.channel, t.location, t.country_code,
            c.full_name AS customer_name, m.merchant_name,
            r.risk_score, r.risk_level,
            ic.id AS case_id, ic.case_status
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        JOIN merchants m ON t.merchant_id = m.id
        JOIN risk_assessments r ON t.id = r.transaction_id
        LEFT JOIN investigation_cases ic ON t.id = ic.transaction_id
        WHERE r.risk_score >= 60
        ORDER BY t.transaction_timestamp DESC
        LIMIT 6
    """)

    # 3. Fetch recent investigation case activities
    recent_activity = query_all("""
        SELECT 
            n.id, n.case_id, n.note_text, n.created_at,
            u.full_name AS author_name,
            c.case_status, c.priority,
            t.transaction_reference
        FROM investigation_notes n
        JOIN users u ON n.user_id = u.id
        JOIN investigation_cases c ON n.case_id = c.id
        JOIN transactions t ON c.transaction_id = t.id
        ORDER BY n.created_at DESC
        LIMIT 5
    """)

    return jsonify({
        "summary": {
            "total_transactions": int(kpi.get("total_transactions") or 0),
            "total_volume": float(kpi.get("total_volume_amount") or 0.0),
            "flagged_transactions": int(kpi.get("flagged_transactions") or 0),
            "flagged_volume": float(kpi.get("flagged_volume_amount") or 0.0),
            "critical_transactions": int(kpi.get("critical_transactions") or 0),
            "pending_cases": int(kpi.get("pending_cases") or 0),
            "confirmed_fraud_cases": int(kpi.get("confirmed_fraud_cases") or 0),
            "fraud_rate": float(kpi.get("fraud_rate_percentage") or 0.0)
        },
        "recent_flagged": recent_flagged,
        "recent_activity": recent_activity
    })

@dashboard_bp.route("/trends", methods=["GET"])
@login_required
def get_trends():
    """Returns daily transaction volume, amount, and flagged counts."""
    trends = query_all("""
        SELECT 
            DATE(t.transaction_timestamp) AS date,
            COUNT(t.id) AS total_count,
            COALESCE(SUM(t.amount), 0.00) AS total_amount,
            COUNT(CASE WHEN r.risk_score >= 60 THEN 1 END) AS flagged_count,
            COALESCE(SUM(CASE WHEN r.risk_score >= 60 THEN t.amount ELSE 0.0 END), 0.00) AS flagged_amount
        FROM transactions t
        LEFT JOIN risk_assessments r ON t.id = r.transaction_id
        GROUP BY DATE(t.transaction_timestamp)
        ORDER BY date ASC
    """)
    return jsonify({"trends": trends})
