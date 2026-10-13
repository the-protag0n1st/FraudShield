-- ============================================================================
-- FraudShield: Academic DBMS Demonstration Queries
-- Suitable for University DBMS Evaluation (BCSE302L Database Systems)
-- ============================================================================

USE fraudshield_db;

-- ----------------------------------------------------------------------------
-- DEMO 1: Multi-Table JOIN with Aggregations, GROUP BY, and HAVING
-- Purpose: Evaluates merchant risk profile by joining 4 tables (merchants, 
--          transactions, risk_assessments, investigation_cases).
-- Filters for merchants with high transaction volume and above-average fraud cases.
-- ----------------------------------------------------------------------------
SELECT 
    m.merchant_name,
    m.category,
    COUNT(t.id) AS total_transactions,
    ROUND(SUM(t.amount), 2) AS total_revenue,
    ROUND(AVG(ra.risk_score), 1) AS avg_risk_score,
    COUNT(CASE WHEN ra.risk_level IN ('high', 'critical') THEN 1 END) AS high_risk_txns,
    COUNT(c.id) AS cases_opened
FROM merchants m
JOIN transactions t ON m.id = t.merchant_id
LEFT JOIN risk_assessments ra ON t.id = ra.transaction_id
LEFT JOIN investigation_cases c ON t.id = c.transaction_id
GROUP BY m.id, m.merchant_name, m.category
HAVING total_transactions >= 2 AND avg_risk_score > 35.0
ORDER BY avg_risk_score DESC, high_risk_txns DESC;


-- ----------------------------------------------------------------------------
-- DEMO 2: Correlated Subquery
-- Purpose: Identifies transactions whose amount exceeds 3x the customer's 
--          historical average amount across prior transactions.
-- ----------------------------------------------------------------------------
SELECT 
    t.id AS txn_id,
    t.transaction_reference,
    c.full_name AS customer_name,
    t.amount AS transaction_amount,
    (
        SELECT ROUND(AVG(prior.amount), 2)
        FROM transactions prior
        WHERE prior.customer_id = t.customer_id
          AND prior.id <> t.id
          AND prior.transaction_timestamp <= t.transaction_timestamp
    ) AS customer_historical_avg,
    t.transaction_timestamp
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE t.amount > 3.0 * (
    SELECT COALESCE(AVG(prior.amount), t.amount)
    FROM transactions prior
    WHERE prior.customer_id = t.customer_id
      AND prior.id <> t.id
      AND prior.transaction_timestamp <= t.transaction_timestamp
)
ORDER BY t.amount DESC;


-- ----------------------------------------------------------------------------
-- DEMO 3: Window Function (Analytical Ranking & Velocity Tracking)
-- Purpose: Computes transaction sequencing and time differences between 
--          consecutive transactions per customer to detect rapid bursts.
-- ----------------------------------------------------------------------------
SELECT 
    t.customer_id,
    cu.full_name AS customer_name,
    t.transaction_reference,
    t.amount,
    t.transaction_timestamp,
    ROW_NUMBER() OVER (
        PARTITION BY t.customer_id 
        ORDER BY t.transaction_timestamp
    ) AS customer_txn_seq,
    TIMESTAMPDIFF(
        MINUTE, 
        LAG(t.transaction_timestamp) OVER (
            PARTITION BY t.customer_id 
            ORDER BY t.transaction_timestamp
        ), 
        t.transaction_timestamp
    ) AS minutes_since_last_txn
FROM transactions t
JOIN customers cu ON t.customer_id = cu.id
ORDER BY t.customer_id, t.transaction_timestamp;


-- ----------------------------------------------------------------------------
-- DEMO 4: View Query Demonstration
-- Purpose: Queries pre-defined relational views (v_dashboard_summary & v_case_overview)
-- ----------------------------------------------------------------------------
-- 4A: Real-time dashboard KPI summary
SELECT * FROM v_dashboard_summary;

-- 4B: Filtered investigation case pipeline
SELECT 
    case_id,
    transaction_reference,
    customer_name,
    merchant_name,
    amount,
    risk_score,
    risk_level,
    case_status,
    priority,
    assigned_to_name
FROM v_case_overview
WHERE case_status IN ('open', 'investigating')
ORDER BY risk_score DESC;


-- ----------------------------------------------------------------------------
-- DEMO 5: Stored Procedure Execution
-- Purpose: Executes atomic transactional update of a case with audit logging.
-- ----------------------------------------------------------------------------
-- Example execution (assuming case ID 1 and investigator user ID 2):
-- CALL sp_update_case_status(1, 2, 'investigating', 'Assigned to analyst for identity verification.');


-- ----------------------------------------------------------------------------
-- DEMO 6: Database Trigger & Audit Immutability Proof
-- Purpose: Proves tamper-evidence of audit logs.
-- Attempting to DELETE or UPDATE an audit log raises SQLSTATE 45000.
-- ----------------------------------------------------------------------------
-- Test query (Expected to FAIL with error code 1644 / SQLSTATE 45000):
-- DELETE FROM audit_logs WHERE id = 1;


-- ----------------------------------------------------------------------------
-- DEMO 7: Query Optimization & EXPLAIN Plan Demonstration
-- Purpose: Validates indexing strategy on composite index (customer_id, transaction_timestamp).
-- ----------------------------------------------------------------------------
EXPLAIN 
SELECT id, amount, transaction_timestamp, transaction_status
FROM transactions
WHERE customer_id = 1
  AND transaction_timestamp >= '2026-10-01 00:00:00'
ORDER BY transaction_timestamp DESC;


-- ----------------------------------------------------------------------------
-- DEMO 8: Explicit Transaction & ACID Rollback Demonstration
-- Purpose: Proves transactional consistency during failure scenarios.
-- ----------------------------------------------------------------------------
START TRANSACTION;

-- Step 1: Insert mock pending transaction
INSERT INTO transactions (
    transaction_reference, customer_id, merchant_id, amount, currency,
    transaction_type, transaction_status, transaction_timestamp, channel,
    location, country_code
) VALUES (
    'TXN-ROLLBACK-TEST', 1, 1, 999.00, 'USD',
    'purchase', 'pending', NOW(), 'online',
    'Test City', 'US'
);

-- Step 2: Attempt illegal insertion violating CHECK constraint (risk_score = 999)
-- This query will fail, leading to rollback:
-- INSERT INTO risk_assessments (transaction_id, risk_score, risk_level) VALUES (LAST_INSERT_ID(), 999, 'critical');

-- Demonstrating explicit rollback
ROLLBACK;

-- Verify that TXN-ROLLBACK-TEST was not committed:
SELECT * FROM transactions WHERE transaction_reference = 'TXN-ROLLBACK-TEST';
