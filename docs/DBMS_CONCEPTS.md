# FraudShield — DBMS Concepts Reference

> [!NOTE]
> Every concept below maps to an **exact file, table, or query** in this repository. No features are invented or inferred.

---

## Concept Map

| # | DBMS Concept | Source File(s) | Key Evidence |
|---|---|---|---|
| 1 | Normalization (1NF / 2NF / 3NF) | `database/schema.sql` | Separate tables, atomic columns, no redundancy |
| 2 | Primary Keys & AUTO_INCREMENT | `database/schema.sql` | All 9 tables use `INT AUTO_INCREMENT PRIMARY KEY` |
| 3 | Foreign Keys & Referential Integrity | `database/schema.sql` | 10 named FK constraints with ON DELETE rules |
| 4 | UNIQUE Constraints | `database/schema.sql` | 6 unique constraints across 6 tables |
| 5 | CHECK Constraints | `database/schema.sql` | 3 CHECK constraints on amount, risk_score, points |
| 6 | Indexes | `database/schema.sql` | 6 named indexes including 2 composite indexes |
| 7 | Views | `database/views.sql` | 3 views: v_dashboard_summary, v_case_overview, v_merchant_risk |
| 8 | Stored Procedure | `database/procedures.sql` | `sp_update_case_status` with input validation & audit |
| 9 | Triggers | `database/triggers.sql` | 3 triggers: resolved_at management + audit immutability |
| 10 | Transactions & Rollback | `backend/db.py` | `get_db_cursor(commit=True)` context manager |
| 11 | Aggregate Queries | `database/views.sql`, `backend/routes/analytics.py` | GROUP BY + COUNT/SUM/AVG/ROUND |
| 12 | Subqueries | `database/views.sql` | Correlated subqueries in `v_dashboard_summary` |
| 13 | Multi-Table JOINs | `database/views.sql`, `backend/fraud_engine.py` | Up to 6-table JOIN in `v_case_overview` |
| 14 | Window Functions | `database/queries.sql` | `ROW_NUMBER() OVER (PARTITION BY ...)` |
| 15 | JSON Data Type | `database/schema.sql`, `database/procedures.sql` | `audit_logs.details JSON`, `JSON_OBJECT()` in SP |
| 16 | INSERT ON DUPLICATE KEY UPDATE | `backend/fraud_engine.py` lines 236–270 | Idempotent upsert of risk_assessments & cases |
| 17 | ENUM Types | `database/schema.sql` | 7 ENUM columns across transactions, risk, cases, users |
| 18 | DECIMAL Type | `database/schema.sql` | `DECIMAL(12,2)` for monetary precision |
| 19 | Parameterized Queries | `backend/fraud_engine.py` + all route files | `%s` placeholders via mysql-connector-python |
| 20 | Password Security | `backend/auth.py`, `tests/unit/test_auth_validation.py` | PBKDF2-SHA256 via Werkzeug |

---

## 1. Normalization

### First Normal Form (1NF)

**Rule:** Every column holds atomic values; no repeating groups.

| Evidence | Detail |
|---|---|
| `risk_factors` table | Each risk factor is stored as a **separate row** linked by `assessment_id` — not as a comma-separated list inside `risk_assessments` |
| All 9 tables | Every column holds a single scalar value (no arrays, no multi-valued fields) |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:** `SELECT * FROM risk_factors WHERE assessment_id = 1;` — observe one row per factor.

---

### Second Normal Form (2NF)

**Rule:** Every non-key attribute depends on the **whole** primary key (no partial dependencies).

| Table | Dependency |
|---|---|
| `risk_factors` | `factor_code`, `description`, `points` all depend entirely on `assessment_id` (single-column PK → 2NF is automatically satisfied) |
| `investigation_notes` | `note_content` depends on the composite (`case_id`, `user_id`, `created_at`) — no partial dependency exists |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

---

### Third Normal Form (3NF)

**Rule:** No transitive dependencies — non-key attributes must depend only on the primary key.

| Non-redundant design | Detail |
|---|---|
| Merchant name & category | Stored exclusively in `merchants` table; `transactions` holds only `merchant_id` FK |
| Customer personal info | Stored exclusively in `customers` table; `transactions` holds only `customer_id` FK |
| No derived storage | `risk_level` is derived from `risk_score` at assessment time and stored only in `risk_assessments` — not repeated elsewhere |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:** `DESCRIBE transactions;` — observe `merchant_id` (FK) not `merchant_name` (would be redundant).

---

## 2. Primary Keys & AUTO_INCREMENT

All 9 tables declare their primary key identically: `INT AUTO_INCREMENT PRIMARY KEY`.

| Table | PK Column | Schema Line |
|---|---|---|
| `users` | `id` | Line 9 |
| `customers` | `id` | Line 20 |
| `merchants` | `id` | Line 30 |
| `transactions` | `id` | Line 40 |
| `risk_assessments` | `id` | Line 62 |
| `risk_factors` | `id` | Line 74 |
| `investigation_cases` | `id` | Line 87 |
| `investigation_notes` | `id` | Line 103 |
| `audit_logs` | `id` | Line 114 |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:** `SHOW CREATE TABLE transactions\G` — inspect `AUTO_INCREMENT` declaration.

---

## 3. Foreign Keys & Referential Integrity

10 named foreign key constraints enforce relational integrity across the schema.

| FK Name | Child Column | References | ON DELETE |
|---|---|---|---|
| `fk_txn_customer` | `transactions.customer_id` | `customers(id)` | `RESTRICT` |
| `fk_txn_merchant` | `transactions.merchant_id` | `merchants(id)` | `RESTRICT` |
| `fk_assess_txn` | `risk_assessments.transaction_id` | `transactions(id)` | `CASCADE` |
| `fk_factor_assess` | `risk_factors.assessment_id` | `risk_assessments(id)` | `CASCADE` |
| `fk_cases_txn` | `investigation_cases.transaction_id` | `transactions(id)` | `CASCADE` |
| `fk_cases_user` | `investigation_cases.assigned_to` | `users(id)` | `SET NULL` |
| `fk_notes_case` | `investigation_notes.case_id` | `investigation_cases(id)` | `CASCADE` |
| `fk_notes_user` | `investigation_notes.user_id` | `users(id)` | `RESTRICT` |
| `fk_audit_user` | `audit_logs.user_id` | `users(id)` | `SET NULL` |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:** Attempt `DELETE FROM transactions WHERE id = 1` while `risk_assessments` row exists → expect `ERROR 1451 (23000): Cannot delete or update a parent row`.

> [!NOTE]
> `ON DELETE CASCADE` propagates deletes down the assessment → factor chain. `ON DELETE SET NULL` preserves orphan audit/case rows without referencing deleted users.

---

## 4. UNIQUE Constraints

| Table | Column | Constraint Purpose |
|---|---|---|
| `users` | `email` | Prevents duplicate accounts |
| `customers` | `customer_reference` | Business-level unique identifier |
| `merchants` | `merchant_reference` | Business-level unique identifier |
| `transactions` | `transaction_reference` | Prevents duplicate transaction ingestion |
| `risk_assessments` | `transaction_id` | Enforces one assessment per transaction |
| `investigation_cases` | `transaction_id` | Enforces one case per transaction |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:** `INSERT INTO risk_assessments (transaction_id, ...) VALUES (1, ...)` twice — second insert raises `ERROR 1062 (23000): Duplicate entry`.

---

## 5. CHECK Constraints

| Table | Column | CHECK Expression | Purpose |
|---|---|---|---|
| `transactions` | `amount` | `amount > 0` | Rejects zero/negative monetary amounts |
| `risk_assessments` | `risk_score` | `risk_score BETWEEN 0 AND 100` | Clamps score to valid range |
| `risk_factors` | `points` | `points > 0` | Ensures every factor contributes positive weight |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:** `INSERT INTO transactions (..., amount) VALUES (..., -50.00)` → expect `ERROR 3819 (HY000): Check constraint violated`.

---

## 6. Indexes

| Index Name | Table | Columns | Type | Usage |
|---|---|---|---|---|
| `idx_txn_cust_time` | `transactions` | `(customer_id, transaction_timestamp)` | Composite | All 4 fraud engine history queries |
| `idx_txn_time` | `transactions` | `(transaction_timestamp)` | Single | Dashboard trend queries |
| `idx_txn_status` | `transactions` | `(transaction_status)` | Single | Status-filtered list queries |
| `idx_assess_level` | `risk_assessments` | `(risk_level)` | Single | Risk-level filtered views |
| `idx_cases_status_priority` | `investigation_cases` | `(case_status, priority)` | Composite | Cases page list queries |
| `idx_audit_entity` | `audit_logs` | `(entity_type, entity_id, created_at)` | Composite | Audit log entity-filtered lookups |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

**Demo:**
```sql
EXPLAIN SELECT * FROM transactions
WHERE customer_id = 1
ORDER BY transaction_timestamp DESC;
```
Observe `key: idx_txn_cust_time` in the EXPLAIN output — confirms index is used.

---

## 7. Views

Three views encapsulate complex query logic and expose clean interfaces to the backend.

| View | Tables Joined | Key Features | Backend Usage |
|---|---|---|---|
| `v_dashboard_summary` | `transactions`, `risk_assessments`, `investigation_cases` (via subqueries) | CASE expressions, correlated subqueries for `pending_cases` and `confirmed_fraud_cases` | `backend/routes/dashboard.py` |
| `v_case_overview` | `investigation_cases` + `transactions` + `customers` + `merchants` + `risk_assessments` + `users` | 6-table JOIN, exposes flattened case row | `backend/routes/cases.py` |
| `v_merchant_risk` | `transactions` + `merchants` + `risk_assessments` | GROUP BY merchant, COUNT + SUM + AVG aggregates | `backend/routes/analytics.py` |

**File:** [`database/views.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/views.sql)

**Demo:**
```sql
SELECT * FROM v_dashboard_summary;
SELECT case_id, customer_name, merchant_name, risk_score, case_status
  FROM v_case_overview ORDER BY risk_score DESC LIMIT 5;
```

---

## 8. Stored Procedure

### `sp_update_case_status`

**File:** [`database/procedures.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/procedures.sql)

| Step | Action |
|---|---|
| 1 | Input validation — rejects invalid `p_new_status` values via `SIGNAL SQLSTATE` |
| 2 | Role-based authorization — checks caller's `users.role` against allowed transitions |
| 3 | Atomic UPDATE — sets `investigation_cases.case_status` |
| 4 | INSERT — writes note row into `investigation_notes` |
| 5 | INSERT — writes `CASE_STATUS_UPDATED` record into `audit_logs` using `JSON_OBJECT()` |

**Backend call site:** [`backend/routes/cases.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/routes/cases.py) — `cursor.callproc('sp_update_case_status', [...])`

**Demo:**
```sql
CALL sp_update_case_status(1, 1, 'investigating', 'Demo note');
SELECT * FROM investigation_notes WHERE case_id = 1 ORDER BY created_at DESC LIMIT 1;
SELECT * FROM audit_logs WHERE action = 'CASE_STATUS_UPDATED' ORDER BY created_at DESC LIMIT 1;
```

---

## 9. Triggers

**File:** [`database/triggers.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/triggers.sql)

| Trigger Name | Event | Timing | Action |
|---|---|---|---|
| `trg_case_resolved_at` | UPDATE on `investigation_cases` | BEFORE UPDATE | Sets `resolved_at = NOW()` when status transitions to a resolved state; clears it when transitioning back to open/investigating |
| `trg_audit_logs_no_update` | UPDATE on `audit_logs` | BEFORE UPDATE | Raises `SIGNAL SQLSTATE '45000'` — prevents any modification to audit records |
| `trg_audit_logs_no_delete` | DELETE on `audit_logs` | BEFORE DELETE | Raises `SIGNAL SQLSTATE '45000'` — prevents deletion of audit records |

**Demo (trigger proof):**
```sql
-- Trigger 1: resolved_at auto-management
CALL sp_update_case_status(1, 1, 'resolved_fraud', 'Confirmed fraud');
SELECT resolved_at FROM investigation_cases WHERE id = 1;  -- should be non-NULL

-- Trigger 2 & 3: tamper-evident protection
DELETE FROM audit_logs WHERE id = 1;  -- expect ERROR 45000 'immutable'
UPDATE audit_logs SET action = 'TAMPERED' WHERE id = 1;  -- expect ERROR 45000
```

---

## 10. Transactions & Rollback

**File:** [`backend/db.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/db.py)

The `get_db_cursor(commit=True)` context manager wraps all database-mutating operations:

- On **success**: `conn.commit()` is called automatically at context exit.
- On **exception**: `conn.rollback()` is called automatically — no partial writes persist.
- The `score_and_persist_assessment` function in [`backend/fraud_engine.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/fraud_engine.py) additionally uses a `SELECT ... FOR UPDATE` lock to prevent concurrent double-scoring of the same transaction.

> [!IMPORTANT]
> All route handlers that write to the database (`POST /api/transactions`, `PATCH /api/cases/{id}`, etc.) acquire their connection through this context manager, ensuring atomicity.

---

## 11. Aggregate Queries

| Location | Aggregation Used | Purpose |
|---|---|---|
| `v_merchant_risk` | `COUNT(*)`, `SUM(amount)`, `AVG(risk_score)`, `ROUND(...)` | Per-merchant fraud statistics |
| `v_dashboard_summary` | `COUNT(*)` with `CASE` expressions | KPI counts by status and risk level |
| `backend/routes/analytics.py` | `GROUP BY` + `COUNT` / `AVG` | Trend and distribution data for charts |
| `backend/routes/dashboard.py` | `GROUP BY date` + `COUNT` | 30-day daily transaction volume |

**Demo:**
```sql
SELECT merchant_name, total_transactions, total_flagged,
       ROUND(avg_risk_score, 1) AS avg_risk
FROM v_merchant_risk
ORDER BY total_flagged DESC LIMIT 10;
```

---

## 12. Subqueries

**File:** [`database/views.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/views.sql)

`v_dashboard_summary` uses correlated subqueries to compute:

| Subquery Result | Correlation |
|---|---|
| `pending_cases` count | Correlated to current date range |
| `confirmed_fraud_cases` count | Correlated to `case_status = 'resolved_fraud'` |

**Demo:** `SELECT * FROM v_dashboard_summary;` — the `pending_cases` and `confirmed_fraud_cases` columns are computed via subquery, not a simple GROUP BY.

---

## 13. Multi-Table JOINs

| Query / View | Tables Joined | Join Count |
|---|---|---|
| `v_case_overview` | `investigation_cases` ⋈ `transactions` ⋈ `customers` ⋈ `merchants` ⋈ `risk_assessments` ⋈ `users` | 6 |
| `fetch_transaction_history` in `fraud_engine.py` | `transactions` ⋈ `merchants` ⋈ `customers` | 3 |

**Demo:**
```sql
SELECT case_id, customer_name, merchant_name, risk_score, case_status
FROM v_case_overview
ORDER BY risk_score DESC
LIMIT 5;
```

---

## 14. Window Functions

**File:** [`database/queries.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/queries.sql)

```sql
ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY transaction_timestamp DESC)
```

Used to rank transactions per customer by recency — demonstrates the `OVER (PARTITION BY ...)` window function syntax.

**Demo:** Run the relevant query from `database/queries.sql` and observe per-customer row numbering.

---

## 15. JSON Data Type

| Location | Usage |
|---|---|
| `audit_logs.details` column | Declared as `JSON` type in `database/schema.sql` |
| `sp_update_case_status` | Builds payload with `JSON_OBJECT('old_status', p_old_status, 'new_status', p_new_status, ...)` before inserting into `audit_logs.details` |

**Demo:**
```sql
SELECT id, action, JSON_PRETTY(details) AS details
FROM audit_logs
WHERE action = 'CASE_STATUS_UPDATED'
ORDER BY created_at DESC LIMIT 1;
```

---

## 16. INSERT ON DUPLICATE KEY UPDATE

**File:** [`backend/fraud_engine.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/fraud_engine.py) — lines 236–270

`score_and_persist_assessment` uses upsert semantics for two tables:

```sql
INSERT INTO risk_assessments (transaction_id, risk_score, risk_level, is_flagged)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
  risk_score = VALUES(risk_score),
  risk_level = VALUES(risk_level),
  is_flagged  = VALUES(is_flagged);
```

The same pattern applies to `investigation_cases`. This guarantees idempotency — calling the scoring function twice on the same transaction produces exactly one assessment row and at most one case row (verified by integration test IT-03).

---

## 17. ENUM Types

| Table | Column | ENUM Values |
|---|---|---|
| `transactions` | `transaction_type` | e.g. `'purchase'`, `'refund'`, `'withdrawal'` |
| `transactions` | `transaction_status` | e.g. `'completed'`, `'failed'`, `'pending'` |
| `transactions` | `channel` | e.g. `'online'`, `'in_store'`, `'atm'` |
| `risk_assessments` | `risk_level` | `'low'`, `'medium'`, `'high'`, `'critical'` |
| `investigation_cases` | `case_status` | `'open'`, `'investigating'`, `'resolved_fraud'`, `'resolved_legitimate'` |
| `investigation_cases` | `priority` | `'low'`, `'medium'`, `'high'`, `'critical'` |
| `users` | `role` | `'admin'`, `'analyst'`, `'viewer'` |

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

Using ENUM provides database-level validation — MySQL rejects any insert that does not match a declared value.

---

## 18. DECIMAL Type

| Table | Column | Type | Rationale |
|---|---|---|---|
| `transactions` | `amount` | `DECIMAL(12,2)` | Exact decimal arithmetic — no floating-point rounding errors |
| `risk_assessments` | (score-related monetary fields) | `DECIMAL(12,2)` | Consistent precision for financial comparisons |

> [!CAUTION]
> Using `FLOAT` or `DOUBLE` for monetary amounts introduces rounding errors. `DECIMAL(12,2)` stores up to 10 digits before the decimal point with exactly 2 decimal places — always exact.

**File:** [`database/schema.sql`](file:///c:/Users/akhil/Downloads/DBMS-DA2/database/schema.sql)

---

## 19. Parameterized Queries (SQL Injection Prevention)

**Files:** All backend route and engine files, e.g. [`backend/fraud_engine.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/fraud_engine.py), [`backend/routes/cases.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/routes/cases.py)

All SQL statements use `%s` placeholders with the `mysql-connector-python` driver. User-supplied values are **never** interpolated via Python string formatting.

```python
# Safe — parameterized
cursor.execute(
    "SELECT * FROM transactions WHERE customer_id = %s AND amount > %s",
    (customer_id, min_amount)
)

# Never done — vulnerable to SQL injection
# cursor.execute(f"SELECT * FROM transactions WHERE customer_id = {customer_id}")
```

---

## 20. Password Security

**Files:** [`backend/auth.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/backend/auth.py), [`tests/unit/test_auth_validation.py`](file:///c:/Users/akhil/Downloads/DBMS-DA2/tests/unit/test_auth_validation.py)

| Function | Library | Algorithm |
|---|---|---|
| `hash_password(password)` | Werkzeug `generate_password_hash` | PBKDF2-SHA256 with salt |
| `verify_password(hash, password)` | Werkzeug `check_password_hash` | Constant-time comparison |

Password hashes begin with the prefix `pbkdf2:sha256:` — raw passwords are never stored. Verified by unit test **UT-01**.

**Demo:** `SELECT email, LEFT(password_hash, 20) FROM users LIMIT 3;` — observe `pbkdf2:sha256:` prefix; no plaintext.
