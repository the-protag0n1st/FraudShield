# FraudShield — Test Results

## Test Run Summary

| Property | Value |
|---|---|
| Test runner | pytest 9.1.1 |
| Python version | 3.14.3 |
| Total tests | 16 |
| Passed | 16 |
| Failed | 0 |
| Exit code | 0 |
| Total execution time | 5.27 s |
| Integration DB | `fraudshield_test` |

---

## Full Test Results

| Test ID | Module | Test Name | Scenario | Expected Result | Actual Result | Status | Execution Time |
|---|---|---|---|---|---|---|---|
| UT-01 | `tests/unit/test_auth_validation.py` | `test_password_hashing` | Hash a raw password; verify with correct password, wrong password, and empty string | Hash has `pbkdf2:sha256` prefix; correct → `True`; wrong → `False`; empty → `False` | All three assertions passed | ✅ PASSED | — |
| UT-02 | `tests/unit/test_fraud_engine.py` | `test_risk_level_boundaries` | Test risk tier classification at all boundary values: 0, 29, 30, 59, 60, 79, 80, 100 | Correct tier label (`low`/`medium`/`high`/`critical`) at each boundary | Correct tier returned at every boundary | ✅ PASSED | — |
| UT-03 | `tests/unit/test_fraud_engine.py` | `test_rule_a_high_amount` | Transaction amount = $7,500 (≥ $5,000 threshold) | `score = 25`, `rule_code = RULE_A_HIGH_AMOUNT` triggered | Score = 25, RULE_A_HIGH_AMOUNT present in factors | ✅ PASSED | — |
| UT-04 | `tests/unit/test_fraud_engine.py` | `test_rule_b_velocity_burst` | `recent_10m_count = 3` (meets threshold of 3) | `score = 20`, `RULE_B_HIGH_VELOCITY` triggered | Score = 20, RULE_B_HIGH_VELOCITY present in factors | ✅ PASSED | — |
| UT-05 | `tests/unit/test_fraud_engine.py` | `test_rule_c_amount_spike` | Transaction amount = $1,500 vs. customer average = $300 (ratio 5.0×, threshold 3.0×) | `score = 20`, `RULE_C_AMOUNT_SPIKE` triggered | Score = 20, RULE_C_AMOUNT_SPIKE present in factors | ✅ PASSED | — |
| UT-06 | `tests/unit/test_fraud_engine.py` | `test_rule_c_skips_when_insufficient_history` | `prior_count = 1`, which is below `min_history_count = 3` | `RULE_C_AMOUNT_SPIKE` NOT triggered | RULE_C absent from factors list | ✅ PASSED | — |
| UT-07 | `tests/unit/test_fraud_engine.py` | `test_rule_d_failed_attempts` | `recent_failed_count = 2` (meets threshold of 2) | `score = 15`, `RULE_D_FAILED_ATTEMPTS` triggered | Score = 15, RULE_D_FAILED_ATTEMPTS present in factors | ✅ PASSED | — |
| UT-08 | `tests/unit/test_fraud_engine.py` | `test_rule_e_novel_merchant` | 0 prior transactions with this merchant; `prior_count = 6 ≥ 3` (established customer) | `score = 10`, `RULE_E_NEW_MERCHANT` triggered | Score = 10, RULE_E_NEW_MERCHANT present in factors | ✅ PASSED | — |
| UT-09 | `tests/unit/test_fraud_engine.py` | `test_rule_f_location_mismatch` | `country_code = 'FR'` vs. last known country `'US'`, within 60 minutes | `score = 20`, `RULE_F_LOCATION_MISMATCH` triggered | Score = 20, RULE_F_LOCATION_MISMATCH present in factors | ✅ PASSED | — |
| UT-10 | `tests/unit/test_fraud_engine.py` | `test_critical_combo_capped_at_100` | All 6 rules fire simultaneously; raw accumulated score = 110 pts | `score = 100` (capped), `risk_level = critical`, `is_flagged = True`, `len(factors) = 6` | Score = 100, risk_level = critical, is_flagged = True, 6 factors returned | ✅ PASSED | — |
| IT-01 | `tests/integration/test_db_workflows.py` | `test_health_check_endpoint` | `GET /api/health` | HTTP 200; response body `{status: healthy, database: connected}` | HTTP 200 received; body matched expected shape | ✅ PASSED | — |
| IT-02 | `tests/integration/test_db_workflows.py` | `test_auth_login_and_session` | (1) `POST /api/auth/login` with invalid credentials → 401; (2) valid admin credentials → 200 + `csrf_token`; (3) `GET /api/auth/me` → authenticated; (4) `POST /api/auth/logout`; (5) re-`GET /api/auth/me` → not authenticated | All five sub-assertions pass in sequence | All five steps passed | ✅ PASSED | — |
| IT-03 | `tests/integration/test_db_workflows.py` | `test_assessment_idempotency_and_no_duplicate_cases` | Score the same transaction twice (call `score_and_persist_assessment` twice with identical inputs) | Exactly 1 row in `risk_assessments` for the transaction; 0 or 1 row in `investigation_cases` | 1 assessment row confirmed; case row count ≤ 1 | ✅ PASSED | — |
| IT-04 | `tests/integration/test_db_workflows.py` | `test_stored_procedure_case_transition_and_audit` | Call `sp_update_case_status` via `cursor.callproc` to transition case to `resolved_fraud` | `investigation_cases.case_status = 'resolved_fraud'`; `resolved_at ≠ NULL`; `audit_logs` contains row with `action = 'CASE_STATUS_UPDATED'` | All three post-conditions verified in DB | ✅ PASSED | — |
| IT-05 | `tests/integration/test_db_workflows.py` | `test_database_trigger_audit_immutability` | `DELETE FROM audit_logs WHERE id = N` (where N is a known audit log row) | MySQL raises `SQLSTATE 45000`; exception message contains `'immutable'` | `DatabaseError` raised; `'immutable'` found in exception string | ✅ PASSED | — |
| IT-06 | `tests/integration/test_db_workflows.py` | `test_transaction_creation_and_automatic_case` | INSERT a transaction with `amount = $9,500` then call `score_and_persist_assessment` | `risk_score ≥ 25`; if `risk_score ≥ 60` then an `investigation_cases` row exists with `case_status = 'open'` | Risk score ≥ 25 confirmed; case row with `status = open` found | ✅ PASSED | — |

---

## Notes

- **Unit tests (UT-01 → UT-10)** run entirely in-memory with mock database context — no live DB connection required.
- **Integration tests (IT-01 → IT-06)** connect to a dedicated `fraudshield_test` database and exercise the full application stack including stored procedures, triggers, and session management.
- Individual per-test execution times are not emitted by default in this pytest configuration; the aggregate wall-clock time was **5.27 s**.
- To reproduce: `py -m pytest tests/ -v` from the project root.
