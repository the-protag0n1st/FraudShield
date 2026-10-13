# FraudShield — Report Screenshot Checklist

> [!IMPORTANT]
> All 18 screenshots must be captured from the **live running application**. Do not use placeholder images or edited screenshots. Capture in order where possible — some screens depend on prior actions (e.g., screenshot 10 requires screenshot 9 to have been completed first).

---

## Browser Screenshots (Application UI)

| # | Screen / Action | Exact URL or Command | Suggested Caption | DBMS Concept Demonstrated |
|---|---|---|---|---|
| 1 | Login page | `http://localhost:5173` | *"FraudShield login page with demo quick-fill buttons"* | Password security; session authentication |
| 2 | Dashboard — KPI stat cards | `http://localhost:5173/dashboard` | *"Dashboard KPI cards: total transactions, flagged count, critical count, pending cases, fraud rate"* | Aggregate queries; `v_dashboard_summary` view |
| 3 | Dashboard — 30-day trend chart | `http://localhost:5173/dashboard` (scroll down to chart) | *"30-day daily transaction volume — area chart powered by GROUP BY DATE aggregate"* | Aggregate queries; `idx_txn_time` index |
| 4 | Transactions page — table with risk badges | `http://localhost:5173/transactions` | *"Transaction list showing colour-coded risk badge column (low / medium / high / critical)"* | ENUM type for `risk_level`; indexed queries |
| 5 | Transaction drawer — high-risk transaction open | Click any CRITICAL row on the Transactions page | *"Transaction detail drawer: risk score, risk level, and triggered risk factors with descriptions"* | Stored risk_factors rows; 1NF; FK cascade |
| 6 | ScenarioBar — all 5 demo buttons visible | `http://localhost:5173/transactions` | *"ScenarioBar with 5 fraud scenario demo buttons"* | Demo entry point for fraud engine |
| 7 | New transaction — CRITICAL badge in table | After clicking "International Fraud" in ScenarioBar | *"Newly created transaction appearing in table with CRITICAL risk badge"* | INSERT ON DUPLICATE KEY UPDATE; fraud engine |
| 8 | Cases page — case list with priority and status | `http://localhost:5173/cases` | *"Investigation cases list with status (open/investigating/resolved) and priority indicators"* | ENUM types; `idx_cases_status_priority` index; `v_case_overview` |
| 9 | Case detail — open case with risk context and note thread | Click any open case on Cases page | *"Case detail view: transaction context, risk score, assigned analyst, and note thread"* | 6-table JOIN (`v_case_overview`); `investigation_notes` FK |
| 10 | Case resolved — `resolved_at` timestamp populated | After transitioning case to `resolved_fraud` via UI | *"Case status updated to resolved_fraud; resolved_at timestamp auto-set by trg_case_resolved_at trigger"* | `trg_case_resolved_at` BEFORE UPDATE trigger |
| 11 | Analytics page — risk distribution + merchant table | `http://localhost:5173/analytics` | *"Analytics page: risk level pie chart and top-merchant risk table from v_merchant_risk view"* | `v_merchant_risk` view; GROUP BY aggregates |
| 12 | Audit Logs page — CASE_STATUS_UPDATED entries | `http://localhost:5173/audit-logs` | *"Audit log entries showing CASE_STATUS_UPDATED and TRANSACTION_ASSESSED actions with JSON details"* | JSON data type; `audit_logs` table; stored procedure |

---

## MySQL Terminal Screenshots

| # | Screen / Action | Exact Command | Suggested Caption | DBMS Concept Demonstrated |
|---|---|---|---|---|
| 13 | `v_dashboard_summary` query output | `SELECT * FROM v_dashboard_summary\G` | *"v_dashboard_summary view output — multi-table aggregation with correlated subqueries"* | Views; aggregate queries; subqueries |
| 14 | `v_case_overview` query output | `SELECT * FROM v_case_overview LIMIT 3\G` | *"v_case_overview output — 6-table JOIN producing flattened case rows"* | Multi-table JOINs (6 tables); views |
| 15 | Stored procedure call + note verification | `CALL sp_update_case_status(1, 1, 'investigating', 'demo');` then `SELECT * FROM investigation_notes WHERE case_id=1 ORDER BY created_at DESC LIMIT 1\G` | *"sp_update_case_status stored procedure: atomic status update, note insert, and audit log insert"* | Stored procedures; transactions; JSON_OBJECT() |
| 16 | Trigger blocking DELETE on audit_logs | `DELETE FROM audit_logs WHERE id=1;` | *"trg_audit_logs_no_delete trigger raises SQLSTATE 45000 — audit records are immutable"* | Triggers; tamper-evident audit |
| 17 | pytest output — 16 passed | `py -m pytest tests/ -v` (from project root) | *"All 16 tests passing: 10 unit + 6 integration; total time 5.27s"* | Full test coverage |
| 18 | `SHOW CREATE TABLE transactions` output | `SHOW CREATE TABLE transactions\G` | *"transactions table DDL: FK constraints, CHECK(amount>0), DECIMAL(12,2), ENUM types, and composite indexes"* | Foreign keys; CHECK constraints; DECIMAL; ENUM; indexes |

---

## Capture Tips

> [!TIP]
> - Use **full-screen** or **windowed** captures at a consistent resolution (e.g. 1920×1080).
> - For MySQL terminal screenshots, increase font size to 14pt+ so output is readable in the report.
> - Screenshot 5 (transaction drawer) and screenshot 9 (case detail) should show **enough rows/data** to be meaningful — run some demo scenarios first if the database is empty.
> - Screenshots 14–16 benefit from using `\G` (vertical output format) instead of tabular, for readability in the report.

> [!NOTE]
> Screenshots 13–18 are MySQL terminal captures — they do not require the React frontend to be visible. A plain terminal window or MySQL Workbench query result pane is sufficient.
