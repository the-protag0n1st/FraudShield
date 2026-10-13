from flask import Blueprint, jsonify
from backend.auth import login_required
from backend.db import query_all

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/overview", methods=["GET"])
@login_required
def get_analytics_overview():
    # 1. Risk tier distribution
    risk_distribution = query_all("""
        SELECT 
            COALESCE(r.risk_level, 'unassessed') AS risk_level,
            COUNT(t.id) AS count,
            COALESCE(SUM(t.amount), 0.00) AS total_amount
        FROM transactions t
        LEFT JOIN risk_assessments r ON t.id = r.transaction_id
        GROUP BY r.risk_level
        ORDER BY FIELD(r.risk_level, 'low', 'medium', 'high', 'critical')
    """)

    # 2. Channel distribution
    channel_distribution = query_all("""
        SELECT 
            t.channel,
            COUNT(t.id) AS count,
            COALESCE(SUM(t.amount), 0.00) AS total_amount,
            COUNT(CASE WHEN r.risk_score >= 60 THEN 1 END) AS flagged_count
        FROM transactions t
        LEFT JOIN risk_assessments r ON t.id = r.transaction_id
        GROUP BY t.channel
        ORDER BY count DESC
    """)

    # 3. Transaction status distribution
    status_distribution = query_all("""
        SELECT 
            t.transaction_status AS status,
            COUNT(t.id) AS count,
            COALESCE(SUM(t.amount), 0.00) AS total_amount
        FROM transactions t
        GROUP BY t.transaction_status
    """)

    # 4. Case resolution breakdown
    case_outcomes = query_all("""
        SELECT 
            case_status,
            priority,
            COUNT(*) AS count
        FROM investigation_cases
        GROUP BY case_status, priority
    """)

    return jsonify({
        "risk_distribution": risk_distribution,
        "channel_distribution": channel_distribution,
        "status_distribution": status_distribution,
        "case_outcomes": case_outcomes
    })

@analytics_bp.route("/risk-distribution", methods=["GET"])
@login_required
def get_risk_distribution():
    data = query_all("""
        SELECT 
            CASE 
                WHEN r.risk_score BETWEEN 0 AND 29 THEN 'Low (0-29)'
                WHEN r.risk_score BETWEEN 30 AND 59 THEN 'Medium (30-59)'
                WHEN r.risk_score BETWEEN 60 AND 79 THEN 'High (60-79)'
                WHEN r.risk_score BETWEEN 80 AND 100 THEN 'Critical (80-100)'
            END AS score_bucket,
            COUNT(t.id) AS transaction_count,
            COALESCE(SUM(t.amount), 0.00) AS total_volume
        FROM transactions t
        JOIN risk_assessments r ON t.id = r.transaction_id
        GROUP BY score_bucket
        ORDER BY MIN(r.risk_score) ASC
    """)
    return jsonify({"distribution": data})

@analytics_bp.route("/top-merchants", methods=["GET"])
@login_required
def get_top_merchants():
    data = query_all("""
        SELECT *
        FROM v_merchant_risk
        ORDER BY flagged_count DESC, total_transactions DESC
        LIMIT 10
    """)
    return jsonify({"merchants": data})

@analytics_bp.route("/resolution-rates", methods=["GET"])
@login_required
def get_resolution_rates():
    data = query_all("""
        SELECT 
            case_status,
            COUNT(*) AS count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM investigation_cases), 1) AS percentage
        FROM investigation_cases
        GROUP BY case_status
    """)
    return jsonify({"resolution_rates": data})
