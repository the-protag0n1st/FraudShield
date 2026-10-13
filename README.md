# FraudShield — Financial Transaction Fraud Detection & Investigation Simulator

[![Python 3.14+](https://img.shields.io/badge/Python-3.14+-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL 8](https://img.shields.io/badge/MySQL-8.4_InnoDB-4479a1?logo=mysql&logoColor=white)](https://mysql.com)
[![React 18](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4-646cff?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tests Passing](https://img.shields.io/badge/pytest-16_passed-success?logo=pytest&logoColor=white)](https://pytest.org)

FraudShield is a full-stack financial transaction risk monitoring and fraud investigation platform built for university database systems evaluations (BCSE302L). It combines a normalized MySQL 8 InnoDB relational database with a deterministic heuristic risk engine, a Flask parameterized REST API, and a React dark fintech analyst console.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              React 18 + Vite (Port 5173)                   │
│  Dark Fintech UI • Recharts • Lucide • Real-Time Scenarios  │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON / Same-Origin Cookie Session
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Flask 3 REST API (Port 5000)                │
│   Auth & CSRF • Pure Scoring Engine • Parameterized SQL     │
└──────────────────────────────┬──────────────────────────────┘
                               │ mysql-connector-python (%s)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 MySQL 8.4 Server (Port 3306)                │
│  InnoDB • Views • Stored Procedures • Triggers • Check Keys │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory Tech Stack & Guardrails

- **Database**: MySQL 8.4 (InnoDB tables, Foreign Keys, CHECK constraints, Composite Indexes, 3 Views, 1 Stored Procedure, 3 Triggers).
- **Backend**: Python 3.14, Flask, `mysql-connector-python` with raw parameterized `%s` queries, Werkzeug password hashing, Flask cookie sessions.
- **Strictly Prohibited & Omitted**: No ORM (No SQLAlchemy, No PyMySQL), No JWTs, No external cloud ML APIs.
- **Frontend**: React 18, Vite, React Router, Recharts, Lucide React, Custom Dark CSS System.

---

## 3. Demo Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin@fraudshield.local` | `Admin@123` | Full Access, Reopen Resolved Cases, Audit View |
| **Lead Analyst** | `investigator@fraudshield.local` | `Investigator@123` | Case Investigation, Add Notes, Resolve Cases |
| **Risk Analyst** | `marcus@fraudshield.local` | `Investigator@123` | Case Investigation, Add Notes, Resolve Cases |

---

## 4. Quick Start Guide

### Step 1: Configure Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
Ensure your MySQL server credentials match `.env`:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=fraudshield_db
DB_TEST_NAME=fraudshield_test
SECRET_KEY=dev-secret-key-fraudshield-2026-secure
FRONTEND_ORIGIN=http://localhost:5173
```

### Step 2: Initialize Database & Seed Synthetic Demo Dataset
```bash
# Seed development database with 130 pre-scored transactions and cases
py scripts/seed.py

# (Optional) Seed integration test database
py scripts/seed.py fraudshield_test
```

### Step 3: Run Backend API Server
```bash
py backend/app.py
```
Backend API starts on `http://127.0.0.1:5000`. Verify health:
```bash
curl http://127.0.0.1:5000/api/health
```

### Step 4: Run Frontend Console
In a separate terminal:
```bash
cd frontend
npm run dev
```
Open your browser at **`http://localhost:5173`**.

---

## 5. Fraud Detection Rules Engine (`backend/fraud_engine.py`)

Deterministic and explainable heuristic rule set:

| Rule Code | Rule Name | Points | Condition |
|---|---|---|---|
| `RULE_A_HIGH_AMOUNT` | High Transaction Amount | +25 pts | Amount $\ge \$5,000.00$ |
| `RULE_B_HIGH_VELOCITY` | Rapid Transaction Velocity | +20 pts | $\ge 3$ transactions in preceding 10 minutes |
| `RULE_C_AMOUNT_SPIKE` | Unusual Amount Spike | +20 pts | Amount $\ge 3.0\times$ customer's historical average ($\ge 3$ prior txns) |
| `RULE_D_FAILED_ATTEMPTS`| Repeated Failed Attempts | +15 pts | $\ge 2$ declined transactions in preceding 30 minutes |
| `RULE_E_NEW_MERCHANT` | Novel Merchant Interaction | +10 pts | Customer has never transacted with this merchant ($\ge 3$ prior txns) |
| `RULE_F_LOCATION_MISMATCH`| Location Inconsistency | +20 pts | Country code differs from recent transaction within 60 minutes |

### Risk Tiers
- **Low**: 0–29 points
- **Medium**: 30–59 points
- **High**: 60–79 points *(Automatically generates an Investigation Case)*
- **Critical**: 80–100 points *(Automatically generates a Critical Case)*

---

## 6. Academic DBMS Features & Verification

- **Schema Definition**: [`database/schema.sql`](database/schema.sql)
- **Database Views**: [`database/views.sql`](database/views.sql) (`v_dashboard_summary`, `v_case_overview`, `v_merchant_risk`)
- **Stored Procedures**: [`database/procedures.sql`](database/procedures.sql) (`sp_update_case_status`)
- **Database Triggers**: [`database/triggers.sql`](database/triggers.sql) (`trg_case_resolved_at`, `trg_audit_logs_no_update`, `trg_audit_logs_no_delete`)
- **Demonstration Queries**: [`database/queries.sql`](database/queries.sql)
- **ER Diagram & Normalization**: [`docs/ER_DIAGRAM.md`](docs/ER_DIAGRAM.md)
- **DBMS Concepts Mapping**: [`docs/DBMS_CONCEPTS.md`](docs/DBMS_CONCEPTS.md)
- **Presentation Demo Script**: [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)

---

## 7. Running Tests

Run the full automated test suite with pytest:
```bash
py -m pytest tests/ -v
```

Output:
```
tests/integration/test_db_workflows.py::test_health_check_endpoint PASSED
tests/integration/test_db_workflows.py::test_auth_login_and_session PASSED
tests/integration/test_db_workflows.py::test_assessment_idempotency_and_no_duplicate_cases PASSED
tests/integration/test_db_workflows.py::test_stored_procedure_case_transition_and_audit PASSED
tests/integration/test_db_workflows.py::test_database_trigger_audit_immutability PASSED
tests/integration/test_db_workflows.py::test_transaction_creation_and_automatic_case PASSED
tests/unit/test_auth_validation.py::test_password_hashing PASSED
tests/unit/test_fraud_engine.py::test_risk_level_boundaries PASSED
tests/unit/test_fraud_engine.py::test_rule_a_high_amount PASSED
tests/unit/test_fraud_engine.py::test_rule_b_velocity_burst PASSED
tests/unit/test_fraud_engine.py::test_rule_c_amount_spike PASSED
tests/unit/test_fraud_engine.py::test_rule_c_skips_when_insufficient_history PASSED
tests/unit/test_fraud_engine.py::test_rule_d_failed_attempts PASSED
tests/unit/test_fraud_engine.py::test_rule_e_novel_merchant PASSED
tests/unit/test_fraud_engine.py::test_rule_f_location_mismatch PASSED
tests/unit/test_fraud_engine.py::test_critical_combo_capped_at_100 PASSED

============================= 16 passed in 4.93s =============================
```
