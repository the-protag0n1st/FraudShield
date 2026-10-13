# FraudShield — Transaction & Fraud Scoring Sequence Diagram

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Browser
    participant Flask
    participant FraudEngine
    participant MySQL

    Browser->>Flask: POST /api/transactions (amount, customer_id, merchant_id, country, ...)

    Flask->>Flask: Validate input fields & CSRF token

    Flask->>MySQL: INSERT INTO transactions (customer_id, merchant_id, amount, currency, country, status, transaction_time)
    MySQL-->>Flask: transaction_id

    Flask->>FraudEngine: score_and_persist_assessment(cursor, transaction_id)

    FraudEngine->>MySQL: SELECT transactions JOIN merchants JOIN customers WHERE transaction_id = ? FOR UPDATE
    MySQL-->>FraudEngine: transaction row (locked)

    FraudEngine->>MySQL: SELECT general stats — COUNT(*), AVG(amount), SUM(...) FROM transactions WHERE customer_id = ?
    MySQL-->>FraudEngine: lifetime stats

    FraudEngine->>MySQL: SELECT velocity — COUNT(*) FROM transactions WHERE customer_id = ? AND transaction_time >= NOW() - INTERVAL 10 MINUTE
    MySQL-->>FraudEngine: recent_10m_count

    FraudEngine->>MySQL: SELECT failed — COUNT(*) FROM transactions WHERE customer_id = ? AND status = 'failed' AND transaction_time >= NOW() - INTERVAL 30 MINUTE
    MySQL-->>FraudEngine: recent_failed_count

    FraudEngine->>MySQL: SELECT location — MAX(country) FROM transactions WHERE customer_id = ? AND transaction_time >= NOW() - INTERVAL 60 MINUTE AND transaction_id != ?
    MySQL-->>FraudEngine: last_recent_country

    FraudEngine->>FraudEngine: evaluate_rules() — pure Python, accumulate score + factors list

    Flask->>MySQL: INSERT INTO risk_assessments (transaction_id, risk_score, risk_level, assessed_at) ON DUPLICATE KEY UPDATE risk_score = VALUES(risk_score), risk_level = VALUES(risk_level)
    MySQL-->>Flask: assessment_id

    Flask->>MySQL: DELETE FROM risk_factors WHERE assessment_id = ?
    Flask->>MySQL: INSERT INTO risk_factors (assessment_id, factor_name, description, score_contribution) [one row per triggered factor]

    alt risk_score >= 60
        Flask->>MySQL: INSERT INTO investigation_cases (transaction_id, case_status, priority, opened_at) ON DUPLICATE KEY UPDATE priority = VALUES(priority)
        Note over MySQL: trg_case_resolved_at BEFORE UPDATE fires on status changes — sets/clears resolved_at automatically
        MySQL-->>Flask: case_id
    end

    Flask->>MySQL: INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, performed_at)
    Note over MySQL: trg_audit_logs_no_update and trg_audit_logs_no_delete prevent any modification or deletion of audit records
    MySQL-->>Flask: OK

    MySQL-->>Flask: assessment result (risk_score, risk_level, factors, case_id)

    Flask-->>Browser: JSON { transaction_id, risk_score, risk_level, factors, case_id, is_flagged }
```

---

## Step-by-Step Narrative

| Step | Actor | Action |
|---|---|---|
| 1 | Browser → Flask | HTTP POST to `/api/transactions` carrying transaction fields in the JSON body along with the CSRF token. |
| 2 | Flask | Validates all required fields and checks the CSRF token before touching the database. |
| 3 | Flask → MySQL | Inserts the new transaction row and receives the auto-generated `transaction_id`. |
| 4 | Flask → FraudEngine | Calls `score_and_persist_assessment`, passing the active cursor and the new `transaction_id`. |
| 5 | FraudEngine → MySQL | Locks the transaction row with `SELECT … FOR UPDATE` to prevent concurrent scoring races, joining `merchants` and `customers` for context. |
| 6–9 | FraudEngine → MySQL | Executes four aggregate queries to build the customer's historical context: lifetime stats, 10-minute velocity, 30-minute failure rate, and 60-minute location window. |
| 10 | FraudEngine | Runs `evaluate_rules()` — a pure-Python function with no further I/O — and produces a final score (0–100) and a list of triggered factor objects. |
| 11 | Flask → MySQL | Upserts the `risk_assessments` record using `ON DUPLICATE KEY UPDATE` to handle reprocessing safely. |
| 12 | Flask → MySQL | Clears and re-inserts `risk_factors` rows to keep them in sync with the current score. |
| 13 | Flask → MySQL | If `risk_score ≥ 60`, upserts an `investigation_cases` record. The `trg_case_resolved_at` trigger fires automatically on any status-column UPDATE to manage the `resolved_at` timestamp. |
| 14 | Flask → MySQL | Writes an `audit_logs` record. The `trg_audit_logs_no_update` and `trg_audit_logs_no_delete` triggers ensure no one can alter or erase audit entries after they are written. |
| 15 | MySQL → Flask | Returns the persisted assessment data. |
| 16 | Flask → Browser | Returns a JSON response containing `transaction_id`, `risk_score`, `risk_level`, `factors`, `case_id` (or `null`), and `is_flagged`. |
