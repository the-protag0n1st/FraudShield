-- ============================================================================
-- FraudShield: Database Views
-- Provides high-performance consolidated read models for APIs and dashboards
-- ============================================================================

-- 1. Dashboard summary aggregation view
CREATE OR REPLACE VIEW v_dashboard_summary AS
SELECT
    COUNT(t.id) AS total_transactions,
    COALESCE(SUM(t.amount), 0.00) AS total_volume_amount,
    COALESCE(SUM(CASE WHEN r.risk_score >= 60 THEN 1 ELSE 0 END), 0) AS flagged_transactions,
    COALESCE(SUM(CASE WHEN r.risk_score >= 60 THEN t.amount ELSE 0.00 END), 0.00) AS flagged_volume_amount,
    COALESCE(SUM(CASE WHEN r.risk_level = 'critical' THEN 1 ELSE 0 END), 0) AS critical_transactions,
    (SELECT COUNT(*) FROM investigation_cases WHERE case_status IN ('open', 'investigating')) AS pending_cases,
    (SELECT COUNT(*) FROM investigation_cases WHERE case_status = 'resolved_fraud') AS confirmed_fraud_cases,
    ROUND(
        CASE 
            WHEN COUNT(t.id) = 0 THEN 0 
            ELSE (COUNT(CASE WHEN r.risk_score >= 60 THEN 1 END) * 100.0 / COUNT(t.id)) 
        END, 2
    ) AS fraud_rate_percentage
FROM transactions t
LEFT JOIN risk_assessments r ON t.id = r.transaction_id;

-- 2. Case Overview consolidated view
CREATE OR REPLACE VIEW v_case_overview AS
SELECT
    c.id AS case_id,
    c.transaction_id,
    t.transaction_reference,
    t.amount,
    t.currency,
    t.channel,
    t.location AS transaction_location,
    t.country_code,
    t.transaction_status,
    t.transaction_timestamp,
    cu.id AS customer_id,
    cu.customer_reference,
    cu.full_name AS customer_name,
    cu.email AS customer_email,
    m.id AS merchant_id,
    m.merchant_reference,
    m.merchant_name,
    m.category AS merchant_category,
    r.risk_score,
    r.risk_level,
    c.case_status,
    c.priority,
    c.assigned_to,
    u.full_name AS assigned_to_name,
    c.resolution_notes,
    c.created_at AS case_created_at,
    c.updated_at AS case_updated_at,
    c.resolved_at
FROM investigation_cases c
JOIN transactions t ON c.transaction_id = t.id
JOIN customers cu ON t.customer_id = cu.id
JOIN merchants m ON t.merchant_id = m.id
LEFT JOIN risk_assessments r ON t.id = r.transaction_id
LEFT JOIN users u ON c.assigned_to = u.id;

-- 3. Merchant Risk Analysis view
CREATE OR REPLACE VIEW v_merchant_risk AS
SELECT
    m.id AS merchant_id,
    m.merchant_reference,
    m.merchant_name,
    m.category,
    COUNT(t.id) AS total_transactions,
    COALESCE(SUM(t.amount), 0.00) AS total_volume,
    COUNT(CASE WHEN r.risk_score >= 60 THEN 1 END) AS flagged_count,
    ROUND(COALESCE(AVG(r.risk_score), 0), 1) AS avg_risk_score,
    COUNT(CASE WHEN r.risk_level = 'critical' THEN 1 END) AS critical_count
FROM merchants m
LEFT JOIN transactions t ON m.id = t.merchant_id
LEFT JOIN risk_assessments r ON t.id = r.transaction_id
GROUP BY m.id, m.merchant_reference, m.merchant_name, m.category;
