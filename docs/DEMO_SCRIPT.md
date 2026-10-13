# FraudShield — Demo Script (5–7 Minutes)

> [!NOTE]
> Rehearse this script at least once before the live presentation. Have all three services started **before** the demo begins.

---

## Pre-Demo Checklist

- [ ] MySQL service is running on port 3306
- [ ] Flask backend is running (`py backend/app.py`)
- [ ] React frontend is running (`npm run dev` in `frontend/`)
- [ ] Browser tab is open at `http://localhost:5173`
- [ ] MySQL Workbench or terminal client is open and connected to `fraudshield`
- [ ] Terminal is ready for pytest run

---

## Section 1 — Setup (≈ 30 seconds)

**Goal:** Show the full stack is live.

Open two terminals side by side.

**Terminal 1 — Flask backend:**
```powershell
cd c:\Users\akhil\Downloads\DBMS-DA2
py backend/app.py
```

**Terminal 2 — React frontend:**
```powershell
cd c:\Users\akhil\Downloads\DBMS-DA2\frontend
npm run dev
```

> [!TIP]
> If both servers are already running, simply show the terminal output to confirm they are active — no need to restart.

**Speaking point:** "We have three services: MySQL on 3306, a Flask REST API serving `/api/*` routes, and a React frontend on port 5173."

Open browser → `http://localhost:5173`

---

## Section 2 — Login (≈ 30 seconds)

**Goal:** Demonstrate session-based authentication.

1. On the login page, click the **Admin Login** quick-fill button.
   - This fills in `admin@fraudshield.local` / `Admin@123`.
2. Click **Sign In**.
3. You will land on the **Dashboard** page.

**Speaking point:** "Passwords are stored as PBKDF2-SHA256 hashes — never plaintext. The backend uses Werkzeug's `generate_password_hash` and `check_password_hash`. Logins are protected by CSRF tokens."

Show the dashboard is now loaded with real data.

---

## Section 3 — Dashboard & Analytics (≈ 45 seconds)

**Goal:** Show aggregate queries and views powering the UI.

1. **Point out the KPI cards** at the top of the dashboard:
   - Total Transactions
   - Flagged Count
   - Critical Count
   - Pending Cases
   - Fraud Rate

   **Speaking point:** "These numbers come from `v_dashboard_summary` — a view that uses `CASE` expressions and correlated subqueries."

2. **Point to the trend chart** (area chart showing 30-day daily transaction volume).

   **Speaking point:** "This chart uses `GROUP BY DATE(transaction_timestamp)` with `COUNT(*)` — a straightforward aggregate query indexed by `idx_txn_time`."

3. **Navigate to the Analytics page** (sidebar).
   - Show the **risk distribution pie chart** — powered by `GROUP BY risk_level`.
   - Show the **top merchants risk table** — powered by `v_merchant_risk` (GROUP BY merchant with COUNT, SUM, AVG aggregates).

---

## Section 4 — Create a Suspicious Transaction (≈ 1 minute)

**Goal:** Trigger the fraud engine and show automatic case creation.

1. Find the **ScenarioBar** (visible on the Transactions page).
2. Click the **"International Fraud"** demo button.

   **Speaking point:** "This sends a `POST /api/transactions/demo/international_fraud` request. The backend inserts a transaction and immediately calls `score_and_persist_assessment`."

3. Watch the new transaction appear in the Transactions table with a **CRITICAL** badge.

4. Click to open the **transaction drawer**:
   - Note the `risk_score` value (≥ 60).
   - Note the `risk_level` = `critical`.
   - Show the **risk factors list**: `RULE_A_HIGH_AMOUNT` (high value) and `RULE_F_LOCATION_MISMATCH` (country mismatch) are both triggered.

   **Speaking point:** "Because the score is ≥ 60, the engine automatically creates an investigation case using `INSERT … ON DUPLICATE KEY UPDATE` — so running the engine twice on the same transaction never creates a duplicate case."

---

## Section 5 — Case Investigation (≈ 1.5 minutes)

**Goal:** Demonstrate the stored procedure, trigger, and investigation workflow.

1. **Navigate to the Cases page** (sidebar).
2. Find the newly created case (status: `open`, priority: `high` or `critical`).
3. Open the case detail view.

**First status transition:**
4. Change the status dropdown from `open` → `investigating`.
5. Add a note: `"Reviewing transaction with issuer bank"`.
6. Click **Save**.

   **Speaking point:** "Clicking Save sends `PATCH /api/cases/{id}` to the backend, which calls `cursor.callproc('sp_update_case_status', [...])` — our MySQL stored procedure. The procedure validates the transition, atomically updates the case status, inserts the note into `investigation_notes`, and writes a `CASE_STATUS_UPDATED` entry to `audit_logs` using `JSON_OBJECT()`."

**Second status transition:**
7. Change status from `investigating` → `resolved_fraud`.
8. Add a resolution note: `"Confirmed fraudulent transaction — card blocked"`.
9. Click **Save**.

10. Observe the **`resolved_at`** timestamp is now populated.

    **Speaking point:** "The `resolved_at` field was set automatically by the `trg_case_resolved_at` trigger — a `BEFORE UPDATE` trigger on `investigation_cases`. The application never sets this field directly."

---

## Section 6 — Audit Trail (≈ 30 seconds)

**Goal:** Show the tamper-evident audit log.

1. **Navigate to the Audit Logs page** (sidebar).
2. Show entries with `action = CASE_STATUS_UPDATED` — each has a JSON `details` column showing `old_status` and `new_status`.
3. Also show `TRANSACTION_ASSESSED` entries from the fraud engine.

**Speaking point:** "The `audit_logs` table is protected by two triggers: `trg_audit_logs_no_update` and `trg_audit_logs_no_delete`. Any attempt to modify or delete an audit record raises MySQL SIGNAL SQLSTATE 45000. We'll prove this in the SQL demo."

---

## Section 7 — SQL Demo (≈ 1 minute)

**Goal:** Show raw SQL demonstrating views, stored procedure, trigger enforcement.

Open a MySQL terminal or Workbench query tab connected to the `fraudshield` database.

Run each query and narrate:

```sql
-- 1. Dashboard view (multi-table aggregation + correlated subqueries)
SELECT * FROM v_dashboard_summary;
```
*"One SELECT from the view — internally it aggregates across transactions, risk_assessments, and investigation_cases."*

```sql
-- 2. Case overview (6-table JOIN)
SELECT case_id, customer_name, merchant_name, risk_score, case_status
FROM v_case_overview
ORDER BY risk_score DESC
LIMIT 5;
```
*"This view joins 6 tables: investigation_cases, transactions, customers, merchants, risk_assessments, and users."*

```sql
-- 3. Trigger proof: attempt to delete an audit log — will fail
DELETE FROM audit_logs WHERE id = 1;
```
*"The `trg_audit_logs_no_delete` trigger immediately fires and raises SQLSTATE 45000. No row is deleted."*

```sql
-- 4. Call stored procedure directly
CALL sp_update_case_status(1, 1, 'investigating', 'Demo note from SQL');
```
*"The procedure validates inputs, updates the case, inserts a note, and writes to audit_logs atomically."*

---

## Section 8 — Tests (≈ 30 seconds)

**Goal:** Show the automated test suite passing.

Switch to a terminal in the project root:

```powershell
py -m pytest tests/ -v
```

**Expected output:**
```
tests/unit/test_auth_validation.py::test_password_hashing           PASSED
tests/unit/test_fraud_engine.py::test_risk_level_boundaries         PASSED
tests/unit/test_fraud_engine.py::test_rule_a_high_amount            PASSED
tests/unit/test_fraud_engine.py::test_rule_b_velocity_burst         PASSED
tests/unit/test_fraud_engine.py::test_rule_c_amount_spike           PASSED
tests/unit/test_fraud_engine.py::test_rule_c_skips_when_insufficient_history PASSED
tests/unit/test_fraud_engine.py::test_rule_d_failed_attempts        PASSED
tests/unit/test_fraud_engine.py::test_rule_e_novel_merchant         PASSED
tests/unit/test_fraud_engine.py::test_rule_f_location_mismatch      PASSED
tests/unit/test_fraud_engine.py::test_critical_combo_capped_at_100  PASSED
tests/integration/test_db_workflows.py::test_health_check_endpoint  PASSED
tests/integration/test_db_workflows.py::test_auth_login_and_session PASSED
tests/integration/test_db_workflows.py::test_assessment_idempotency_and_no_duplicate_cases PASSED
tests/integration/test_db_workflows.py::test_stored_procedure_case_transition_and_audit PASSED
tests/integration/test_db_workflows.py::test_database_trigger_audit_immutability PASSED
tests/integration/test_db_workflows.py::test_transaction_creation_and_automatic_case PASSED

16 passed in 5.27s
```

**Speaking point:** "10 unit tests cover the fraud engine rules and authentication in isolation. 6 integration tests run against the live `fraudshield_test` database and verify stored procedures, triggers, idempotency, and session management end-to-end."
