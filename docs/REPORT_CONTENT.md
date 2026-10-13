# FraudShield — Transaction Fraud Detection and Investigation Simulator
## Academic Project Report

---

## Cover Page

| Field | Details |
|---|---|
| **Project Title** | FraudShield — Transaction Fraud Detection and Investigation Simulator |
| **Course** | Database Systems |
| **Course Code** | BCSE302L |
| **Faculty** | Parvathy A K |
| **Institution** | Vellore Institute of Technology, Vellore |
| **Student Name** | Pandilla S Akhila |
| **Register Number** | 24BCE1240 |
| **Submitted In Partial Fulfilment of** | DA-2 Project Assessment |

---

## Table of Contents

1. Abstract
2. Introduction & Problem Statement
3. Objectives, Scope, Requirements, and Limitations
4. Existing Approaches & Proposed System
5. System Architecture
6. Database Design & Normalization
7. Data Dictionary
8. Constraints, Indexes, and Foreign Keys
9. Fraud Scoring Algorithm
10. Flask API & Frontend Implementation
11. Security Measures
12. Testing Methodology & Test Results
13. Conclusion & Future Enhancements
14. References
15. Appendix Checklist

---

## 1. Abstract

FraudShield is a full-stack, database-driven web application that simulates real-time transaction fraud detection and structured case investigation. The system ingests financial transactions, evaluates each one against a deterministic, rule-based fraud engine, and automatically escalates high-risk events into investigation cases that trained investigators can triage, annotate, and resolve.

The backend is built on Python 3 with the Flask micro-framework and communicates with a MySQL 8 InnoDB database through parameterized queries and a stored procedure. The frontend is a single-page application built with React 18 and Vite, presenting live dashboards, paginated transaction and case tables, analytics charts, and an admin panel through a Bootstrap 5 and Recharts-powered interface.

The database schema comprises nine tables normalized to Third Normal Form (3NF), three analytical views, three data-integrity triggers, and one transactional stored procedure. A suite of sixteen automated tests — ten unit tests and six integration tests — all passed, validating both the fraud-scoring logic and the end-to-end database workflows. The system demonstrates practical application of relational database concepts including normalization, referential integrity, role-based access control, immutable audit logging, and parameterized query security.

---

## 2. Introduction & Problem Statement

### 2.1 Background

Financial fraud is among the most costly and rapidly evolving threats facing institutions globally. Card-not-present fraud, account takeover, and transaction velocity attacks account for billions of dollars in annual losses. Detection systems must operate in or near real time, produce explainable risk scores, and integrate tightly with human investigator workflows so that flagged events are resolved quickly and accurately.

University-level database systems courses require students to demonstrate mastery of relational design, SQL, normalization theory, and the integration of a database backend with an application layer. A fraud detection simulator provides a rich, realistic domain that exercises all of these skills: complex multi-table schemas, analytical views and aggregations, triggers for data integrity, stored procedures for business logic, and a REST API layer that enforces security constraints.

### 2.2 Problem Statement

Existing teaching examples in DBMS courses are often limited to simple CRUD applications (e.g., library or hospital management systems) that do not expose students to: (a) event-driven database objects such as triggers, (b) procedural logic encapsulated in stored procedures, (c) analytical views that aggregate across multiple fact and dimension tables, or (d) a fraud-specific scoring algorithm whose results drive application workflow.

FraudShield addresses this gap by implementing a complete, production-inspired fraud detection pipeline — from transaction ingestion and automated risk scoring, through case creation and investigator assignment, to audit-logged resolution — within a well-normalized relational schema.

### 2.3 Domain Context

A payment transaction involves a **customer**, a **merchant**, an **amount**, a channel (online, POS, mobile, ATM), a geographic location, and a timestamp. Fraud signals emerge from anomalies in these dimensions: an unusually large amount, abnormally high transaction velocity, a sudden shift in geography, a previously unknown merchant, or repeated declined attempts. FraudShield models exactly these signals as explicit, versioned scoring rules and persists both the aggregate score and the individual rule contributions for every assessed transaction.

---

## 3. Objectives, Scope, Requirements, and Limitations

### 3.1 Objectives

1. Design and implement a fully normalized (3NF) relational schema in MySQL 8 InnoDB for a transaction fraud detection domain.
2. Implement three database views that support dashboard analytics and case management without duplicating computation in application code.
3. Implement three triggers that enforce data integrity rules — specifically automated timestamp management and immutable audit log protection.
4. Implement one stored procedure that encapsulates the multi-step, role-validated case status transition workflow atomically.
5. Build a deterministic, rule-based fraud scoring engine in Python with six explicit rules and produce explainable, per-rule score contributions.
6. Expose all functionality through a secure REST API (Flask) with session authentication, CSRF protection, and parameterized SQL.
7. Deliver a React-based single-page application with dashboards, analytics charts, transaction management, case investigation, and an admin panel.
8. Achieve 100% pass rate across sixteen automated tests covering both unit-level logic and integration-level database workflows.

### 3.2 Scope

**In scope:**
- Transaction creation and fraud assessment (automated and manual re-assessment).
- Rule-based risk scoring with six explicitly defined rules and explainable per-rule contributions.
- Automated investigation case creation for transactions scoring ≥ 60.
- Case lifecycle management (open → investigating → resolved_fraud / resolved_legitimate), with admin-only reopen capability.
- Role-based access control (admin vs. investigator).
- Immutable audit logging for all state-changing operations.
- Dashboard, analytics, and admin views.
- Seed dataset of 130 synthetic transactions and 7 investigation cases.

**Out of scope:**
- Machine-learning-based fraud scoring.
- Real payment gateway integration.
- Real-time streaming data ingestion.
- Multi-currency conversion.
- External identity verification.

### 3.3 Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall allow authenticated users to create transactions and immediately receive a risk score and risk level. |
| FR-02 | The system shall automatically create an investigation case for any transaction with a risk score ≥ 60. |
| FR-03 | The system shall persist per-rule score contributions (rule code, points, explanation) alongside the aggregate assessment. |
| FR-04 | Investigators shall be able to view all open and assigned cases, add notes, and update case status. |
| FR-05 | Only admin-role users shall be able to reopen a resolved case. |
| FR-06 | The system shall maintain an immutable audit log of all status changes and note additions. |
| FR-07 | The dashboard shall display aggregate statistics sourced from the `v_dashboard_summary` view. |
| FR-08 | The analytics section shall display risk distribution, daily volume, merchant risk rankings, and an hourly heatmap. |
| FR-09 | The admin panel shall expose user, customer, merchant, and audit log management. |

### 3.4 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | All passwords shall be hashed with PBKDF2-SHA256 via Werkzeug; plaintext passwords shall never be stored. |
| NFR-02 | All SQL queries shall use parameterized placeholders; no string-formatted SQL shall be used. |
| NFR-03 | CSRF tokens shall be validated for all state-changing API requests. |
| NFR-04 | The database schema shall achieve Third Normal Form (3NF). |
| NFR-05 | All referential integrity constraints shall be enforced at the database level via foreign keys. |
| NFR-06 | The application shall pass all 16 automated tests before submission. |

### 3.5 Limitations

1. **Rule-based only**: The fraud engine uses hand-crafted threshold rules; it does not employ statistical or machine-learning models. Precision and recall on real-world data have not been measured.
2. **Single currency**: All amounts are treated as USD equivalents; no currency conversion logic is implemented.
3. **No real-time streaming**: Transaction ingestion is synchronous via REST API, not an event-driven stream (e.g., Kafka).
4. **Simulated data**: The 130-transaction seed dataset is synthetic and generated deterministically; it does not represent real cardholder behaviour.
5. **Single-node deployment**: No clustering, replication, or high-availability configuration has been implemented.

---

## 4. Existing Approaches & Proposed System

### 4.1 Existing Approaches

**Rule-Based Engines (Traditional)**
Legacy fraud systems used hand-crafted threshold rules (e.g., "decline if amount > $10,000"). These are transparent and auditable but brittle: thresholds must be tuned manually and do not adapt to evolving fraud patterns.

**Statistical Models**
Logistic regression and decision-tree models trained on historical labelled transactions can generalize better than fixed rules but require large labelled datasets, regular retraining, and careful feature engineering. Their outputs can be harder to explain to investigators.

**Machine Learning / Deep Learning**
Gradient-boosted trees (XGBoost, LightGBM) and neural networks achieve high AUC-ROC on benchmark fraud datasets. However, they are black-box models, require substantial infrastructure (feature stores, model registries, retraining pipelines), and their predictions can be difficult to justify in regulatory contexts.

**Graph-Based Methods**
Graph neural networks and link-analysis techniques identify fraud rings by modelling relationships between accounts, devices, and merchants. These are the state-of-the-art in large financial institutions but are operationally complex.

### 4.2 Proposed System

FraudShield adopts a **deterministic, rule-based scoring engine** for educational clarity and auditability. Every point added to a transaction's risk score is traceable to a named rule with an explicit condition and a fixed point value. This design:

- Produces fully explainable assessments (a requirement in regulated industries under GDPR Article 22 and similar frameworks).
- Requires no training data or model lifecycle management.
- Is straightforward to extend: adding a new rule requires inserting a new condition block in `fraud_engine.py` and incrementing `RULES_VERSION`.
- Stores per-rule contributions in `risk_factors`, enabling investigators to understand exactly why a transaction was flagged.

The proposed system integrates the fraud engine tightly with a relational database that manages the full investigation lifecycle, creating an end-to-end pipeline from transaction ingestion to case resolution.

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
│         React 18 + Vite SPA (Bootstrap 5, Recharts)         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON  (X-CSRF-Token header)
┌──────────────────────────▼──────────────────────────────────┐
│                   Flask REST API (Python 3)                  │
│  blueprints: auth · transactions · cases · analytics · admin │
│  before_request: session check + CSRF validation             │
│  fraud_engine.py: rule evaluation + scoring                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ mysql-connector-python (%s params)
┌──────────────────────────▼──────────────────────────────────┐
│                   MySQL 8 InnoDB Database                    │
│  9 Tables · 3 Views · 3 Triggers · 1 Stored Procedure       │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Component Descriptions

| Component | Technology | Responsibility |
|---|---|---|
| Frontend SPA | React 18 + Vite + React Router | Routing, UI rendering, API calls |
| UI Framework | Bootstrap 5 | Layout, responsive design, components |
| Charts | Recharts | Bar, line, pie, and heatmap visualizations |
| Icons | Lucide React | Icon set |
| API Server | Flask (Python 3) | REST endpoint handling, session management |
| Password Hashing | Werkzeug | PBKDF2-SHA256 hashing and verification |
| Environment | python-dotenv | `.env` loading for secrets |
| DB Driver | mysql-connector-python | Parameterized query execution |
| Database | MySQL 8 InnoDB | Persistent storage, integrity, views, triggers |
| Test Runner | pytest 9.1.1 | Unit and integration test execution |

### 5.3 Data Flow: Transaction Ingestion & Assessment

```
Client POSTs /api/transactions
      │
      ▼
Flask validates session + CSRF token
      │
      ▼
Insert row into `transactions`
      │
      ▼
fraud_engine.assess_transaction(transaction_id)
      │
      ├─ Query customer history (avg amount, prior count)
      ├─ Query velocity (recent 10-min count)
      ├─ Query failed attempts (recent 30-min declined count)
      ├─ Query merchant history (prior transactions with merchant)
      ├─ Query location history (last transaction country in 60 min)
      ├─ Evaluate RULE_A through RULE_F
      ├─ Cap total score at 100
      ├─ Determine risk_level
      ├─ INSERT into risk_assessments
      └─ INSERT into risk_factors (one row per triggered rule)
      │
      ▼
If score ≥ 60:
      └─ INSERT into investigation_cases (status='open', priority=risk_level)
      │
      ▼
INSERT into audit_logs
      │
      ▼
Return transaction + assessment + factors to client
```

---

## 6. Database Design & Normalization

### 6.1 Entity-Relationship Overview

The schema models a **fraud investigation domain** with the following primary entities and relationships:

- A **Customer** makes one or more **Transactions**.
- A **Transaction** targets one **Merchant**.
- A **Transaction** has at most one **RiskAssessment** (1-to-1, enforced by UNIQUE constraint on `transaction_id`).
- A **RiskAssessment** has zero or more **RiskFactors** (one per triggered rule).
- A **Transaction** may have at most one **InvestigationCase** (1-to-1, UNIQUE on `transaction_id`).
- An **InvestigationCase** may be assigned to a **User** (investigator/admin).
- An **InvestigationCase** has zero or more **InvestigationNotes**, each authored by a **User**.
- All state-changing operations produce **AuditLog** entries, optionally linked to a **User**.

### 6.2 Normalization Analysis

#### 6.2.1 First Normal Form (1NF)

A relation is in 1NF if every attribute contains only atomic (indivisible) values and there are no repeating groups.

**Evidence in FraudShield:**
- Every column in every table holds a single atomic value. For example, `transactions.location` stores a single location string, not a list of locations. If multiple risk rules apply to an assessment, they are stored as separate rows in `risk_factors`, not as a comma-separated list in `risk_assessments`.
- All tables have a defined primary key (`id INT PK AUTO_INCREMENT`).
- ENUM columns (e.g., `transaction_type`, `risk_level`, `case_status`) constrain values to a defined, finite domain — a valid 1NF practice.
- The `audit_logs.details` column stores a JSON value. While JSON is a structured type, MySQL treats the column as atomic at the relational level; its internal structure is opaque to the RDBMS and does not violate 1NF.

#### 6.2.2 Second Normal Form (2NF)

A relation is in 2NF if it is in 1NF and every non-key attribute is fully functionally dependent on the entire primary key (i.e., no partial dependencies — relevant only when the primary key is composite).

**Evidence in FraudShield:**
- All nine tables use a single-column surrogate primary key (`id INT AUTO_INCREMENT`). Because the primary key is never composite, partial dependency is impossible by definition, and all tables trivially satisfy 2NF.
- Natural keys (e.g., `transaction_reference`, `customer_reference`, `merchant_reference`) are declared as UNIQUE constraints — used for business lookups — but are not part of the primary key, preserving 2NF compliance.

#### 6.2.3 Third Normal Form (3NF)

A relation is in 3NF if it is in 2NF and no non-key attribute is transitively dependent on the primary key through another non-key attribute.

**Evidence in FraudShield:**

*Violation avoided — Customer data not in Transactions:*
A naive design might store `customer_full_name` and `customer_email` directly in the `transactions` table. FraudShield instead stores only `customer_id` (a foreign key), with customer attributes living exclusively in the `customers` table. This eliminates the transitive dependency `transaction.id → customer_id → customer_full_name`.

*Violation avoided — Merchant data not in Transactions:*
Similarly, `merchant_name` and `merchant_category` are stored in `merchants`, referenced by `transactions.merchant_id`. There is no transitive dependency through merchant attributes in the transactions table.

*Violation avoided — Risk level not recomputed in RiskFactors:*
`risk_factors` stores `assessment_id`, `rule_code`, `rule_name`, `points`, and `explanation`. It does not store the computed `risk_level` — that lives in `risk_assessments`, its proper functional home.

*Violation avoided — User role not duplicated in InvestigationCases:*
`investigation_cases.assigned_to` is a foreign key to `users.id`. The user's `role` is stored only in `users` and is fetched via JOIN when needed. Role information does not transitively reside in the cases table.

*Violation avoided — Case status not in InvestigationNotes:*
`investigation_notes` stores only `case_id`, `user_id`, `note_text`, and `created_at`. It does not store a snapshot of case status — that is read from `investigation_cases` by JOIN.

All nine tables satisfy 3NF.

---

## 7. Data Dictionary

### 7.1 Table: `users`

Stores system users (administrators and investigators) who log into FraudShield.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `full_name` | VARCHAR(100) | NOT NULL | User's display name |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL | Login identifier; unique across all users |
| `password_hash` | VARCHAR(255) | NOT NULL | PBKDF2-SHA256 hash produced by Werkzeug |
| `role` | ENUM('admin','investigator') | NOT NULL, DEFAULT 'investigator' | Access control role |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft-delete flag; inactive users cannot log in |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

---

### 7.2 Table: `customers`

Stores the cardholders / account holders whose transactions are monitored.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `customer_reference` | VARCHAR(50) | UNIQUE, NOT NULL | External/business-facing customer identifier |
| `full_name` | VARCHAR(100) | NOT NULL | Customer's full name |
| `email` | VARCHAR(120) | NOT NULL | Customer contact email |
| `phone` | VARCHAR(20) | NULL | Optional phone number |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Index:** `idx_cust_ref(customer_reference)` — supports fast lookups by business reference.

---

### 7.3 Table: `merchants`

Stores the merchants at which transactions occur.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `merchant_reference` | VARCHAR(50) | UNIQUE, NOT NULL | External/business-facing merchant identifier |
| `merchant_name` | VARCHAR(100) | NOT NULL | Merchant trading name |
| `category` | VARCHAR(50) | NOT NULL | Business category (e.g., retail, travel) |
| `location` | VARCHAR(100) | NOT NULL | Merchant physical or registered location |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Index:** `idx_merch_cat(category)` — supports category-based analytics queries.

---

### 7.4 Table: `transactions`

Central fact table; records every financial transaction submitted to the system.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `transaction_reference` | VARCHAR(64) | UNIQUE, NOT NULL | Unique external transaction identifier (e.g., UUID) |
| `customer_id` | INT | FK → customers(id) ON DELETE RESTRICT, NOT NULL | Owning customer |
| `merchant_id` | INT | FK → merchants(id) ON DELETE RESTRICT, NOT NULL | Target merchant |
| `amount` | DECIMAL(12,2) | NOT NULL, CHECK (amount > 0) | Transaction amount in base currency |
| `currency` | VARCHAR(3) | NOT NULL, DEFAULT 'USD' | ISO 4217 currency code |
| `transaction_type` | ENUM('purchase','transfer','withdrawal','refund') | NOT NULL | Nature of the transaction |
| `transaction_status` | ENUM('approved','declined','pending') | NOT NULL | Processing outcome |
| `transaction_timestamp` | DATETIME | NOT NULL | When the transaction was initiated |
| `channel` | ENUM('online','pos','mobile','atm') | NOT NULL | Origination channel |
| `location` | VARCHAR(100) | NOT NULL | Geographic location string |
| `country_code` | VARCHAR(2) | NOT NULL, DEFAULT 'US' | ISO 3166-1 alpha-2 country code |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record insertion timestamp |

**Check constraint:** `amount > 0` — prevents zero or negative transaction amounts.

**Indexes:**
- `idx_txn_cust_time(customer_id, transaction_timestamp)` — composite index for velocity and history queries filtered by customer and time window.
- `idx_txn_time(transaction_timestamp)` — supports time-range analytics scans.
- `idx_txn_status(transaction_status)` — supports filtering by status (e.g., counting declined transactions).

---

### 7.5 Table: `risk_assessments`

Stores the aggregate fraud score and risk level for each assessed transaction. One-to-one with `transactions`.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `transaction_id` | INT | UNIQUE, FK → transactions(id) ON DELETE CASCADE, NOT NULL | Owning transaction (1-to-1 enforced by UNIQUE) |
| `risk_score` | INT | NOT NULL, CHECK (risk_score BETWEEN 0 AND 100) | Aggregate fraud score (0–100) |
| `risk_level` | ENUM('low','medium','high','critical') | NOT NULL | Categorical risk label derived from score |
| `rules_version` | VARCHAR(20) | NOT NULL, DEFAULT 'v1.0' | Version of the rule set used for assessment |
| `assessed_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of assessment |

**Check constraint:** `risk_score BETWEEN 0 AND 100` — enforces the score cap at the database level.

**Index:** `idx_assess_level(risk_level)` — supports risk-level distribution queries.

---

### 7.6 Table: `risk_factors`

Stores individual rule contributions for each risk assessment. One-to-many with `risk_assessments`.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `assessment_id` | INT | FK → risk_assessments(id) ON DELETE CASCADE, NOT NULL | Parent assessment |
| `rule_code` | VARCHAR(50) | NOT NULL | Short rule identifier (e.g., 'RULE_A_HIGH_AMOUNT') |
| `rule_name` | VARCHAR(100) | NOT NULL | Human-readable rule name |
| `points` | INT | NOT NULL, CHECK (points > 0) | Points contributed by this rule |
| `explanation` | TEXT | NOT NULL | Plain-language justification for rule trigger |

**Check constraint:** `points > 0` — ensures only positive contributions are stored.

**Indexes:**
- `idx_factors_assessment(assessment_id)` — fast retrieval of all factors for a given assessment.
- `idx_factors_rule(rule_code)` — supports rule-frequency analytics.

---

### 7.7 Table: `investigation_cases`

Manages the lifecycle of fraud investigation cases. One-to-one with `transactions`.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `transaction_id` | INT | UNIQUE, FK → transactions(id) ON DELETE CASCADE, NOT NULL | Associated transaction (1-to-1 enforced by UNIQUE) |
| `assigned_to` | INT | NULL, FK → users(id) ON DELETE SET NULL | Investigator assigned to this case (nullable) |
| `case_status` | ENUM('open','investigating','resolved_fraud','resolved_legitimate') | NOT NULL, DEFAULT 'open' | Current lifecycle state |
| `priority` | ENUM('low','medium','high','critical') | NOT NULL, DEFAULT 'medium' | Case urgency |
| `resolution_notes` | TEXT | NULL | Final resolution summary (populated at resolution) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Case creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp |
| `resolved_at` | DATETIME | NULL | Timestamp when case was resolved (set by trigger) |

**Indexes:**
- `idx_cases_status_priority(case_status, priority)` — supports filtered case list queries (open cases sorted by priority).
- `idx_cases_assigned(assigned_to)` — supports "my cases" queries by investigator.

---

### 7.8 Table: `investigation_notes`

Stores timestamped notes added by investigators or admins during case investigation.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `case_id` | INT | FK → investigation_cases(id) ON DELETE CASCADE, NOT NULL | Parent case |
| `user_id` | INT | FK → users(id) ON DELETE RESTRICT, NOT NULL | Author (user who wrote the note) |
| `note_text` | TEXT | NOT NULL | Free-text note content |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Note creation timestamp |

**Index:** `idx_notes_case(case_id)` — fast retrieval of all notes for a given case.

---

### 7.9 Table: `audit_logs`

Immutable append-only log of all state-changing operations in the system.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT, NOT NULL | Surrogate primary key |
| `user_id` | INT | NULL, FK → users(id) ON DELETE SET NULL | User who performed the action (NULL for system actions) |
| `action` | VARCHAR(60) | NOT NULL | Action label (e.g., 'case_status_updated') |
| `entity_type` | VARCHAR(50) | NOT NULL | Type of entity affected (e.g., 'investigation_case') |
| `entity_id` | INT | NOT NULL | Primary key of the affected entity row |
| `details` | JSON | NULL | Structured supplementary data (before/after values, notes) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Exact time of the logged event |

**Immutability:** BEFORE UPDATE and BEFORE DELETE triggers (`trg_audit_logs_no_update`, `trg_audit_logs_no_delete`) raise `SQLSTATE '45000'` to prevent any modification or removal of audit records.

**Indexes:**
- `idx_audit_entity(entity_type, entity_id, created_at)` — supports per-entity audit history retrieval in chronological order.
- `idx_audit_user(user_id, created_at)` — supports per-user activity timeline queries.

---

## 8. Constraints, Indexes, and Foreign Keys

### 8.1 Primary Keys

All tables use `id INT NOT NULL AUTO_INCREMENT PRIMARY KEY`, providing stable, incrementing surrogate keys that are never exposed as business identifiers.

### 8.2 Unique Constraints

| Table | Column(s) | Purpose |
|---|---|---|
| `users` | `email` | Prevents duplicate user accounts |
| `customers` | `customer_reference` | Ensures each external customer ID is unique |
| `merchants` | `merchant_reference` | Ensures each external merchant ID is unique |
| `transactions` | `transaction_reference` | Prevents duplicate transaction submissions |
| `risk_assessments` | `transaction_id` | Enforces 1-to-1 relationship with transactions |
| `investigation_cases` | `transaction_id` | Enforces 1-to-1 relationship with transactions |

### 8.3 Foreign Keys

```sql
-- transactions → customers (RESTRICT protects customer history)
ALTER TABLE transactions
  ADD CONSTRAINT fk_txn_customer
  FOREIGN KEY (customer_id) REFERENCES customers(id)
  ON DELETE RESTRICT;

-- transactions → merchants (RESTRICT protects merchant history)
ALTER TABLE transactions
  ADD CONSTRAINT fk_txn_merchant
  FOREIGN KEY (merchant_id) REFERENCES merchants(id)
  ON DELETE RESTRICT;

-- risk_assessments → transactions (CASCADE removes assessment with transaction)
ALTER TABLE risk_assessments
  ADD CONSTRAINT fk_assess_txn
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
  ON DELETE CASCADE;

-- risk_factors → risk_assessments (CASCADE removes factors with assessment)
ALTER TABLE risk_factors
  ADD CONSTRAINT fk_factors_assess
  FOREIGN KEY (assessment_id) REFERENCES risk_assessments(id)
  ON DELETE CASCADE;

-- investigation_cases → transactions (CASCADE removes case with transaction)
ALTER TABLE investigation_cases
  ADD CONSTRAINT fk_case_txn
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
  ON DELETE CASCADE;

-- investigation_cases → users (SET NULL preserves case when user is deleted)
ALTER TABLE investigation_cases
  ADD CONSTRAINT fk_case_user
  FOREIGN KEY (assigned_to) REFERENCES users(id)
  ON DELETE SET NULL;

-- investigation_notes → investigation_cases (CASCADE removes notes with case)
ALTER TABLE investigation_notes
  ADD CONSTRAINT fk_notes_case
  FOREIGN KEY (case_id) REFERENCES investigation_cases(id)
  ON DELETE CASCADE;

-- investigation_notes → users (RESTRICT prevents deletion of note authors)
ALTER TABLE investigation_notes
  ADD CONSTRAINT fk_notes_user
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE RESTRICT;

-- audit_logs → users (SET NULL preserves log entry when user is deleted)
ALTER TABLE audit_logs
  ADD CONSTRAINT fk_audit_user
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE SET NULL;
```

### 8.4 Check Constraints

```sql
-- Transactions: amount must be positive
CONSTRAINT chk_amount_positive CHECK (amount > 0)

-- RiskAssessments: score must be within 0–100
CONSTRAINT chk_score_range CHECK (risk_score BETWEEN 0 AND 100)

-- RiskFactors: point contributions must be positive
CONSTRAINT chk_points_positive CHECK (points > 0)
```

### 8.5 Indexes Summary

| Index Name | Table | Columns | Type | Purpose |
|---|---|---|---|---|
| `idx_cust_ref` | `customers` | `customer_reference` | BTree | Fast customer lookup by reference |
| `idx_merch_cat` | `merchants` | `category` | BTree | Category-based analytics |
| `idx_txn_cust_time` | `transactions` | `customer_id, transaction_timestamp` | BTree (composite) | Velocity and history queries |
| `idx_txn_time` | `transactions` | `transaction_timestamp` | BTree | Time-range analytics |
| `idx_txn_status` | `transactions` | `transaction_status` | BTree | Status-filtered queries |
| `idx_assess_level` | `risk_assessments` | `risk_level` | BTree | Risk distribution analytics |
| `idx_factors_assessment` | `risk_factors` | `assessment_id` | BTree | Factor retrieval by assessment |
| `idx_factors_rule` | `risk_factors` | `rule_code` | BTree | Rule frequency analysis |
| `idx_cases_status_priority` | `investigation_cases` | `case_status, priority` | BTree (composite) | Case queue queries |
| `idx_cases_assigned` | `investigation_cases` | `assigned_to` | BTree | Per-investigator case list |
| `idx_notes_case` | `investigation_notes` | `case_id` | BTree | Notes retrieval by case |
| `idx_audit_entity` | `audit_logs` | `entity_type, entity_id, created_at` | BTree (composite) | Per-entity audit history |
| `idx_audit_user` | `audit_logs` | `user_id, created_at` | BTree (composite) | Per-user activity timeline |

### 8.6 Database Views

#### 8.6.1 `v_dashboard_summary`

Aggregates key performance indicators for the main dashboard. Performs a single-pass aggregation over `transactions` LEFT JOINed with `risk_assessments`, with correlated subqueries against `investigation_cases`.

**Columns returned:**
- `total_transactions` — count of all transactions
- `total_volume_amount` — sum of all transaction amounts
- `flagged_transactions` — count of transactions with `risk_score ≥ 60`
- `flagged_volume_amount` — total amount of flagged transactions
- `critical_transactions` — count of transactions with `risk_level = 'critical'`
- `pending_cases` — count of cases in status `'open'` or `'investigating'`
- `confirmed_fraud_cases` — count of cases in status `'resolved_fraud'`
- `fraud_rate_percentage` — `(flagged_transactions / total_transactions) × 100`

#### 8.6.2 `v_case_overview`

Joins `investigation_cases`, `transactions`, `customers`, `merchants`, `risk_assessments`, and `users` into a single flat view used by the case management interface.

**Columns returned:** All `investigation_cases` fields plus `transaction_reference`, `transaction_timestamp`, `amount`, `currency`, `channel`, `transaction_status`, `customer_full_name`, `customer_email`, `merchant_name`, `merchant_category`, `risk_score`, `risk_level`, `assigned_user_name` (from `users`).

#### 8.6.3 `v_merchant_risk`

Groups `transactions` and `risk_assessments` by merchant to produce merchant-level risk metrics.

**Columns returned:** `merchant_id`, `merchant_name`, `category`, `total_transactions`, `total_volume`, `flagged_count` (score ≥ 60), `avg_risk_score`, `critical_count`.

### 8.7 Triggers

#### 8.7.1 `trg_case_resolved_at`

```sql
CREATE TRIGGER trg_case_resolved_at
BEFORE UPDATE ON investigation_cases
FOR EACH ROW
BEGIN
  IF NEW.case_status IN ('resolved_fraud', 'resolved_legitimate')
     AND OLD.case_status NOT IN ('resolved_fraud', 'resolved_legitimate') THEN
    SET NEW.resolved_at = NOW();
  ELSEIF NEW.case_status = 'open'
     AND OLD.case_status IN ('resolved_fraud', 'resolved_legitimate') THEN
    SET NEW.resolved_at = NULL;
  END IF;
END;
```

**Purpose:** Automatically populates `resolved_at` when a case transitions to a resolved state, and clears it if a resolved case is reopened. This ensures `resolved_at` is always consistent with `case_status` without relying on application code to manage it.

#### 8.7.2 `trg_audit_logs_no_update`

```sql
CREATE TRIGGER trg_audit_logs_no_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Audit log records are immutable and cannot be modified.';
END;
```

**Purpose:** Makes the `audit_logs` table append-only at the database level. Any `UPDATE` statement targeting `audit_logs` — regardless of the source — will be rejected with a meaningful error message.

#### 8.7.3 `trg_audit_logs_no_delete`

```sql
CREATE TRIGGER trg_audit_logs_no_delete
BEFORE DELETE ON audit_logs
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Audit log records are immutable and cannot be deleted.';
END;
```

**Purpose:** Complements `trg_audit_logs_no_update` by blocking `DELETE` statements on `audit_logs`, ensuring complete audit trail preservation.

### 8.8 Stored Procedure: `sp_update_case_status`

```sql
CALL sp_update_case_status(
  p_case_id   INT,
  p_user_id   INT,
  p_new_status VARCHAR(30),
  p_notes     TEXT
);
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `p_case_id` | INT | ID of the case to update |
| `p_user_id` | INT | ID of the user making the update |
| `p_new_status` | VARCHAR(30) | Target status value |
| `p_notes` | TEXT | Optional note text to append (NULL to skip) |

**Logic (atomically within a single execution):**

1. **Status validation:** Verifies `p_new_status` is one of `'open'`, `'investigating'`, `'resolved_fraud'`, `'resolved_legitimate'`. Signals error on invalid value.
2. **Case existence check:** Verifies the case with `p_case_id` exists. Signals error if not found.
3. **Admin-only reopen enforcement:** If `p_new_status = 'open'` and the current status is resolved, queries `users.role` for `p_user_id`. If the role is not `'admin'`, signals an authorization error.
4. **Status update:** Executes `UPDATE investigation_cases SET case_status = p_new_status, assigned_to = p_user_id WHERE id = p_case_id`. The `trg_case_resolved_at` trigger fires here to manage `resolved_at`.
5. **Note insertion:** If `p_notes` is not NULL and not empty, inserts a row into `investigation_notes`.
6. **Audit logging:** Inserts a row into `audit_logs` with `action = 'case_status_updated'`, `entity_type = 'investigation_case'`, `entity_id = p_case_id`, and a JSON `details` object containing the old and new status values.

---

## 9. Fraud Scoring Algorithm

### 9.1 Overview

The fraud engine (`backend/fraud_engine.py`) evaluates each transaction against six independent rules. Rules are evaluated sequentially; a rule either fires and adds its fixed point contribution or does not fire. The raw total is capped at 100. The final score determines a risk level and, if the score meets the flagging threshold, triggers automatic investigation case creation.

```
RULES_VERSION = 'v1.0'
SCORE_CAP     = 100
FLAG_THRESHOLD = 60      ← cases created for score ≥ this value
```

### 9.2 Risk Level Thresholds

| Score Range | Risk Level | Action |
|---|---|---|
| 0 – 29 | **Low** | No case created |
| 30 – 59 | **Medium** | No case created |
| 60 – 79 | **High** | Case created (priority = high) |
| 80 – 100 | **Critical** | Case created (priority = critical) |

### 9.3 Rule Definitions

#### RULE_A — High Amount

| Attribute | Value |
|---|---|
| **Rule Code** | `RULE_A_HIGH_AMOUNT` |
| **Points** | +25 |
| **Condition** | `amount ≥ $5,000.00` |
| **Rationale** | Large transactions are statistically associated with higher fraud risk. A fixed threshold of $5,000 captures card-present and card-not-present fraud patterns common in high-value purchase fraud. |

#### RULE_B — High Velocity

| Attribute | Value |
|---|---|
| **Rule Code** | `RULE_B_HIGH_VELOCITY` |
| **Points** | +20 |
| **Condition** | ≥ 3 other transactions by the same customer in the last 10 minutes (excluding the current transaction) |
| **Rationale** | A burst of rapid transactions from a single customer within a short window is a strong indicator of automated fraud or credential stuffing. The 10-minute window and threshold of 3 are calibrated to minimize false positives from legitimate shopping sessions. |

#### RULE_C — Amount Spike

| Attribute | Value |
|---|---|
| **Rule Code** | `RULE_C_AMOUNT_SPIKE` |
| **Points** | +20 |
| **Condition** | `amount ≥ 3.0 × customer_historical_average` AND customer has ≥ 3 prior transactions |
| **Rationale** | An amount that greatly exceeds a customer's established spending pattern suggests the transaction is anomalous. The 3.0× multiplier and minimum history requirement (≥ 3 prior transactions) prevent false positives for new customers with sparse history. |

#### RULE_D — Failed Attempts

| Attribute | Value |
|---|---|
| **Rule Code** | `RULE_D_FAILED_ATTEMPTS` |
| **Points** | +15 |
| **Condition** | ≥ 2 declined transactions by the same customer in the last 30 minutes |
| **Rationale** | Multiple recent declines preceding an approved transaction suggest card testing — fraudsters attempting small or random transactions to verify card validity before executing a large purchase. |

#### RULE_E — New Merchant

| Attribute | Value |
|---|---|
| **Rule Code** | `RULE_E_NEW_MERCHANT` |
| **Points** | +10 |
| **Condition** | 0 prior transactions by this customer with this merchant AND customer has ≥ 3 prior transactions overall |
| **Rationale** | A transaction at a merchant the customer has never used before adds a moderate risk signal, particularly when combined with other indicators. The overall-history requirement prevents penalising genuinely new customers. |

#### RULE_F — Location Mismatch

| Attribute | Value |
|---|---|
| **Rule Code** | `RULE_F_LOCATION_MISMATCH` |
| **Points** | +20 |
| **Condition** | `transaction.country_code` differs from the country code of the customer's most recent transaction within the previous 60 minutes |
| **Rationale** | A geographic jump that is physically impossible (or highly implausible) within the elapsed time is a strong fraud indicator, associated with card cloning, account takeover, or use of a stolen card in a foreign country. |

### 9.4 Scoring Algorithm (Pseudocode)

```python
def assess_transaction(transaction_id):
    txn = fetch_transaction(transaction_id)
    history = fetch_customer_history(txn.customer_id, txn.transaction_timestamp)

    score = 0
    factors = []

    # RULE_A
    if txn.amount >= 5000.00:
        score += 25
        factors.append(("RULE_A_HIGH_AMOUNT", "High Amount Transaction", 25,
                         f"Amount ${txn.amount:,.2f} ≥ $5,000.00 threshold"))

    # RULE_B
    recent_10m = count_recent_transactions(txn.customer_id, minutes=10,
                                           exclude_id=transaction_id)
    if recent_10m >= 3:
        score += 20
        factors.append(("RULE_B_HIGH_VELOCITY", "High Transaction Velocity", 20,
                         f"{recent_10m} transactions in last 10 minutes"))

    # RULE_C
    if history.prior_count >= 3:
        if txn.amount >= 3.0 * history.avg_amount:
            score += 20
            factors.append(("RULE_C_AMOUNT_SPIKE", "Unusual Amount Spike", 20,
                             f"${txn.amount:,.2f} is {txn.amount/history.avg_amount:.1f}× "
                             f"average ${history.avg_amount:,.2f}"))

    # RULE_D
    recent_failed = count_declined_transactions(txn.customer_id, minutes=30)
    if recent_failed >= 2:
        score += 15
        factors.append(("RULE_D_FAILED_ATTEMPTS", "Recent Failed Attempts", 15,
                         f"{recent_failed} declined transactions in last 30 minutes"))

    # RULE_E
    if history.prior_count >= 3:
        merchant_txn_count = count_merchant_transactions(txn.customer_id,
                                                         txn.merchant_id)
        if merchant_txn_count == 0:
            score += 10
            factors.append(("RULE_E_NEW_MERCHANT", "New Merchant", 10,
                             "First transaction with this merchant"))

    # RULE_F
    last_country = get_last_country_within(txn.customer_id,
                                            txn.transaction_timestamp, minutes=60)
    if last_country and last_country != txn.country_code:
        score += 20
        factors.append(("RULE_F_LOCATION_MISMATCH", "Geographic Location Mismatch", 20,
                         f"Country '{txn.country_code}' differs from recent '{last_country}'"))

    # Cap and classify
    score = min(score, 100)
    risk_level = classify_risk(score)

    persist_assessment(transaction_id, score, risk_level, factors)

    if score >= 60:
        create_investigation_case(transaction_id,
                                   priority=risk_level, status='open')
    insert_audit_log(action='transaction_assessed', entity_id=transaction_id)

    return score, risk_level, factors
```

### 9.5 Worked Scoring Example

The following uses synthetic values that are part of the project's demonstration dataset.

**Transaction Parameters:**

| Parameter | Value |
|---|---|
| Amount | $8,500.00 |
| Country Code | `GB` |
| Merchant ID | 99 (customer has 0 prior transactions with this merchant) |
| Customer Historical Average | $420.00 |
| Customer Prior Transaction Count | 8 |
| Transactions in Last 10 Minutes | 3 (excluding this transaction) |
| Declined Transactions in Last 30 Minutes | 2 |
| Last Transaction Country (within 60 min) | `US` |

**Rule Evaluation:**

| Rule | Condition Evaluated | Result | Points Added |
|---|---|---|---|
| RULE_A — High Amount | $8,500.00 ≥ $5,000.00 | ✅ FIRED | +25 |
| RULE_B — High Velocity | 3 ≥ 3 recent transactions | ✅ FIRED | +20 |
| RULE_C — Amount Spike | $8,500 / $420 = 20.24× ≥ 3.0× (8 prior txns ≥ 3) | ✅ FIRED | +20 |
| RULE_D — Failed Attempts | 2 ≥ 2 declined in 30 min | ✅ FIRED | +15 |
| RULE_E — New Merchant | 0 prior transactions with merchant, 8 ≥ 3 prior | ✅ FIRED | +10 |
| RULE_F — Location Mismatch | `'GB'` ≠ `'US'` within 60 min | ✅ FIRED | +20 |
| **Raw Total** | | | **110** |
| **After Cap (min(110, 100))** | | | **100** |

**Outcome:**
- `risk_score = 100`
- `risk_level = 'critical'` (score 80–100)
- Score ≥ 60 → **Investigation case auto-created** with `case_status = 'open'`, `priority = 'critical'`
- All 6 rules fire → 6 rows inserted into `risk_factors`

---

## 10. Flask API & Frontend Implementation

### 10.1 API Blueprint Structure

The Flask application is organized into blueprint modules, each handling a distinct concern:

| Blueprint | Prefix | Description |
|---|---|---|
| `auth` | `/api/auth` | Authentication, session management, CSRF |
| `transactions` | `/api/transactions` | Transaction CRUD and fraud assessment |
| `cases` | `/api/cases` | Case management (reads `sp_update_case_status`) |
| `analytics` | `/api/analytics` | Analytics aggregations and charts data |
| `admin` | `/api/admin` | Admin-only: users, customers, merchants, audit |
| `dashboard` | `/api/dashboard` | Dashboard summary and trends |
| `health` | `/api/health` | Liveness check |

### 10.2 API Endpoint Reference

#### Authentication

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/login` | Authenticate with email + password; returns user object and CSRF token in response; sets session cookie |
| POST | `/api/auth/logout` | Clears server-side session |
| GET | `/api/auth/me` | Returns current session user details and a fresh CSRF token |

#### Health

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Returns `{"status": "ok"}` for liveness checking; CSRF exempt |

#### Dashboard

| Method | Path | Description |
|---|---|---|
| GET | `/api/dashboard/summary` | Queries `v_dashboard_summary` view; returns all aggregate KPIs |
| GET | `/api/dashboard/trends` | Returns daily transaction count and volume for the last 30 days |

#### Transactions

| Method | Path | Description |
|---|---|---|
| GET | `/api/transactions` | Returns paginated, filtered list of transactions with assessment data |
| POST | `/api/transactions` | Creates a new transaction and immediately runs fraud assessment |
| GET | `/api/transactions/{id}` | Returns a single transaction with its `risk_assessment` and `risk_factors` array |
| POST | `/api/transactions/{id}/assess` | Manually re-scores an existing transaction (replaces prior assessment) |
| POST | `/api/transactions/demo/{scenario}` | Creates a pre-configured demo transaction matching a named fraud scenario |

#### Cases

| Method | Path | Description |
|---|---|---|
| GET | `/api/cases` | Returns paginated, filtered investigation case list (uses `v_case_overview`) |
| GET | `/api/cases/{id}` | Returns case detail including all `investigation_notes` |
| PATCH | `/api/cases/{id}` | Updates case status/assignment by calling `sp_update_case_status` |

#### Analytics

| Method | Path | Description |
|---|---|---|
| GET | `/api/analytics/risk-distribution` | Count of assessments grouped by `risk_level` |
| GET | `/api/analytics/daily-volume` | 30-day daily transaction volume from `risk_assessments` JOIN `transactions` |
| GET | `/api/analytics/top-merchants` | Merchant risk data from `v_merchant_risk` view |
| GET | `/api/analytics/hourly-heatmap` | Transaction count grouped by hour-of-day |

#### Admin

| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/audit-logs` | Paginated, filterable audit log (admin role required) |
| GET | `/api/admin/users` | List of all system users |
| GET | `/api/admin/customers` | List of all customers |
| GET | `/api/admin/merchants` | List of all merchants |

### 10.3 Frontend Structure

The React 18 SPA is built with Vite and organized around React Router v6 routes:

| Route | Component | Description |
|---|---|---|
| `/login` | `LoginPage` | Email/password login form; stores CSRF token on success |
| `/dashboard` | `DashboardPage` | KPI cards from `v_dashboard_summary`, trend line chart |
| `/transactions` | `TransactionsPage` | Paginated table with status/risk filters; create transaction modal |
| `/transactions/:id` | `TransactionDetailPage` | Full detail: assessment, rule factors, linked case |
| `/cases` | `CasesPage` | Paginated case queue with status/priority filters |
| `/cases/:id` | `CaseDetailPage` | Case detail: status transitions, notes timeline |
| `/analytics` | `AnalyticsPage` | Risk distribution pie chart, daily volume bar chart, merchant risk table, hourly heatmap |
| `/admin` | `AdminPage` | Tabbed admin panel: users, customers, merchants, audit log |

**Key Frontend Libraries:**
- **React Router v6** — client-side routing with protected route wrappers.
- **Bootstrap 5** — grid layout, cards, tables, modals, badges.
- **Recharts** — BarChart, LineChart, PieChart, and custom heatmap visualizations.
- **Lucide React** — consistent icon set throughout the interface.

---

## 11. Security Measures

### 11.1 Password Security

FraudShield uses **Werkzeug's `generate_password_hash` and `check_password_hash`** functions, which implement PBKDF2-SHA256 with a random salt. Stored hashes carry the prefix `pbkdf2:sha256:` and include the iteration count and salt, making rainbow-table attacks infeasible. Plaintext passwords are never stored, logged, or returned by any API endpoint.

### 11.2 Session Management

Flask's built-in server-side session mechanism is used. The session is keyed by a `SECRET_KEY` loaded from the `.env` file via `python-dotenv`. The `.env` file is excluded from version control via `.gitignore`. Session cookies are HTTP-only and bound to the server's `SECRET_KEY` for tamper detection.

### 11.3 CSRF Protection

A CSRF token is issued at login and included in the `/api/auth/me` response. The React frontend attaches it as an `X-CSRF-Token` HTTP header on all state-changing requests (POST, PATCH, PUT, DELETE). A Flask `before_request` hook validates this header against the session-stored token for all endpoints except `/api/auth/login` and `/api/health` (which are explicitly exempt).

```
Login → CSRF token issued → stored in React state
Subsequent mutating requests → X-CSRF-Token: <token> header → validated in before_request
```

### 11.4 SQL Injection Prevention

All database queries use **parameterized statements** with `%s` placeholders through `mysql-connector-python`. No string formatting, concatenation, or f-strings are used to construct SQL query text. This ensures that user-supplied input is always treated as a value parameter and never as executable SQL.

### 11.5 Role-Based Access Control

Two roles are defined: **admin** and **investigator**. Access control is enforced at two layers:

1. **Flask API layer:** Route handlers check `session['role']` before executing admin-only operations (e.g., `/api/admin/*` endpoints require `role = 'admin'`).
2. **Database layer:** `sp_update_case_status` independently queries `users.role` inside the stored procedure to enforce the admin-only reopen constraint. This prevents privilege escalation even if the API-layer check is bypassed.

### 11.6 Audit Trail

Every state-changing operation (transaction assessment, case status update, note addition) inserts a row into `audit_logs`. Two database triggers (`trg_audit_logs_no_update`, `trg_audit_logs_no_delete`) make these records immutable at the database level, ensuring a tamper-evident audit trail that cannot be altered even by direct database access.

---

## 12. Testing Methodology & Test Results

### 12.1 Test Infrastructure

| Item | Value |
|---|---|
| Test runner | pytest 9.1.1 |
| Python version | 3.14.3 |
| Test database | `fraudshield_test` (isolated MySQL database) |
| Unit test directory | `tests/unit/` |
| Integration test directory | `tests/integration/` |
| Total tests | 16 |
| Tests passed | 16 |
| Tests failed | 0 |

### 12.2 Unit Tests (`tests/unit/`)

Unit tests validate the fraud engine's pure logic and the authentication helper independently of the database, using synthetic input values.

| # | Test File | Test Name | Description | Status |
|---|---|---|---|---|
| 1 | `test_auth_validation.py` | `test_password_hashing` | Verifies Werkzeug `generate_password_hash` produces a valid PBKDF2-SHA256 hash and that `check_password_hash` correctly verifies it | ✅ PASSED |
| 2 | `test_fraud_engine.py` | `test_risk_level_boundaries` | Confirms the `classify_risk` function returns 'low' at score 0 and 29, 'medium' at 30 and 59, 'high' at 60 and 79, 'critical' at 80 and 100 | ✅ PASSED |
| 3 | `test_fraud_engine.py` | `test_rule_a_high_amount` | Verifies RULE_A fires for amounts ≥ $5,000 and does not fire below threshold | ✅ PASSED |
| 4 | `test_fraud_engine.py` | `test_rule_b_velocity_burst` | Verifies RULE_B fires when recent_10m_count ≥ 3 and does not fire at count 2 | ✅ PASSED |
| 5 | `test_fraud_engine.py` | `test_rule_c_amount_spike` | Verifies RULE_C fires when amount ≥ 3.0× avg and prior_count ≥ 3 | ✅ PASSED |
| 6 | `test_fraud_engine.py` | `test_rule_c_skips_when_insufficient_history` | Verifies RULE_C does NOT fire when prior_count < 3, even if amount is large | ✅ PASSED |
| 7 | `test_fraud_engine.py` | `test_rule_d_failed_attempts` | Verifies RULE_D fires when declined count in 30 min ≥ 2 | ✅ PASSED |
| 8 | `test_fraud_engine.py` | `test_rule_e_novel_merchant` | Verifies RULE_E fires for a new merchant when prior_count ≥ 3 | ✅ PASSED |
| 9 | `test_fraud_engine.py` | `test_rule_f_location_mismatch` | Verifies RULE_F fires when country_code differs from the last transaction's country within 60 min | ✅ PASSED |
| 10 | `test_fraud_engine.py` | `test_critical_combo_capped_at_100` | Verifies that when all six rules fire (raw total = 110), the final score is capped at 100 | ✅ PASSED |

### 12.3 Integration Tests (`tests/integration/`)

Integration tests execute against the live `fraudshield_test` MySQL database, exercising end-to-end workflows through the Flask API and verifying database state after each operation.

| # | Test File | Test Name | Description | Status |
|---|---|---|---|---|
| 11 | `test_db_workflows.py` | `test_health_check_endpoint` | Verifies `GET /api/health` returns HTTP 200 and `{"status": "ok"}` | ✅ PASSED |
| 12 | `test_db_workflows.py` | `test_auth_login_and_session` | Posts valid credentials to `POST /api/auth/login`, verifies HTTP 200, user object in response, CSRF token present, and session cookie set | ✅ PASSED |
| 13 | `test_db_workflows.py` | `test_assessment_idempotency_and_no_duplicate_cases` | Re-assesses a transaction twice and verifies only one `risk_assessments` row and at most one `investigation_cases` row exist (no duplicates from re-scoring) | ✅ PASSED |
| 14 | `test_db_workflows.py` | `test_stored_procedure_case_transition_and_audit` | Calls `PATCH /api/cases/{id}` to transition a case from 'open' to 'investigating', then to 'resolved_fraud', verifying: (a) `case_status` and `resolved_at` updated correctly, (b) `sp_update_case_status` inserted an audit log row, (c) note text persisted in `investigation_notes` | ✅ PASSED |
| 15 | `test_db_workflows.py` | `test_database_trigger_audit_immutability` | Directly attempts an `UPDATE` on an `audit_logs` row and a `DELETE`, verifying both raise `SQLSTATE '45000'` errors with the expected message | ✅ PASSED |
| 16 | `test_db_workflows.py` | `test_transaction_creation_and_automatic_case` | Posts a synthetic transaction (all six rules triggered, score = 100) to `POST /api/transactions`, then queries the database to verify: (a) transaction row created, (b) `risk_assessments` row with `risk_score = 100` and `risk_level = 'critical'`, (c) 6 `risk_factors` rows, (d) `investigation_cases` row automatically created with `priority = 'critical'` | ✅ PASSED |

### 12.4 Test Results Summary

```
================================ test session starts ================================
platform win32 -- Python 3.14.3, pytest-9.1.1
collected 16 items

tests/unit/test_auth_validation.py::test_password_hashing           PASSED [ 6%]
tests/unit/test_fraud_engine.py::test_risk_level_boundaries         PASSED [12%]
tests/unit/test_fraud_engine.py::test_rule_a_high_amount            PASSED [18%]
tests/unit/test_fraud_engine.py::test_rule_b_velocity_burst         PASSED [25%]
tests/unit/test_fraud_engine.py::test_rule_c_amount_spike           PASSED [31%]
tests/unit/test_fraud_engine.py::test_rule_c_skips_when_insufficient_history PASSED [37%]
tests/unit/test_fraud_engine.py::test_rule_d_failed_attempts        PASSED [43%]
tests/unit/test_fraud_engine.py::test_rule_e_novel_merchant         PASSED [50%]
tests/unit/test_fraud_engine.py::test_rule_f_location_mismatch      PASSED [56%]
tests/unit/test_fraud_engine.py::test_critical_combo_capped_at_100  PASSED [62%]
tests/integration/test_db_workflows.py::test_health_check_endpoint  PASSED [68%]
tests/integration/test_db_workflows.py::test_auth_login_and_session PASSED [75%]
tests/integration/test_db_workflows.py::test_assessment_idempotency_and_no_duplicate_cases PASSED [81%]
tests/integration/test_db_workflows.py::test_stored_procedure_case_transition_and_audit    PASSED [87%]
tests/integration/test_db_workflows.py::test_database_trigger_audit_immutability           PASSED [93%]
tests/integration/test_db_workflows.py::test_transaction_creation_and_automatic_case       PASSED [100%]

========================== 16 passed in total ==========================
```

---

## 13. Conclusion & Future Enhancements

### 13.1 Conclusion

FraudShield successfully demonstrates the design and implementation of a complete, database-driven financial fraud detection and investigation system within the scope of a university DBMS course project. The following objectives were met:

- **Database Design:** A nine-table relational schema in MySQL 8 InnoDB, fully normalized to Third Normal Form, with 13 secondary indexes, 9 foreign keys, and 3 CHECK constraints enforcing data integrity at the database level.
- **Database Objects:** Three analytical views abstracting complex join logic from application code; three triggers enforcing automated timestamp management and audit immutability; one multi-step, role-validated stored procedure encapsulating the case status transition workflow.
- **Fraud Engine:** A deterministic, six-rule scoring engine that produces scores of 0–100 (capped), assigns risk levels, and generates per-rule explanations stored in `risk_factors`. All six rules are individually tested and collectively validated with a capped-score edge case.
- **Application Layer:** A Flask REST API with 21 endpoints organized into six blueprints, secured with PBKDF2-SHA256 password hashing, session management, CSRF token validation, and parameterized SQL.
- **Frontend:** A React 18 SPA with dashboard, transaction management, case investigation, analytics, and admin interfaces.
- **Testing:** 16 automated tests (10 unit, 6 integration) — all 16 passed — validating fraud engine logic, authentication, stored procedure behaviour, trigger immutability, and end-to-end transaction assessment workflow.
- **Seed Data:** 130 synthetic transactions producing 7 automatically flagged investigation cases (1 critical), a 5.38% fraud rate, and a realistic operational dataset for demonstration.

### 13.2 Future Enhancements

The following enhancements are identified as natural extensions of this work beyond the current project scope:

1. **Machine Learning Integration:** Replace or augment the rule-based engine with a gradient-boosted tree model (e.g., LightGBM) trained on historical labelled transactions. The `risk_factors` table schema could be extended to store feature importance values from the model.

2. **Real-Time Streaming Ingestion:** Replace the synchronous REST-based ingestion with a Kafka consumer pipeline, enabling sub-second assessment latency for high-volume transaction streams.

3. **Graph-Based Fraud Ring Detection:** Model customers, merchants, and transactions as a graph (using Neo4j or a graph extension) to detect linked fraud rings — groups of accounts coordinating fraudulent behaviour that is invisible to per-transaction rules.

4. **Adaptive Thresholds:** Implement customer-specific, dynamically updated thresholds (e.g., using an exponential moving average of `amount`) rather than global fixed thresholds for RULE_A and RULE_C.

5. **Multi-Currency Support:** Add exchange rate data and normalize all amounts to a base currency at ingestion time, enabling accurate cross-currency amount comparisons in RULE_C.

6. **Notification System:** Integrate email or webhook alerts when a critical case is created, enabling real-time paging of on-call investigators.

7. **Case Assignment Rules:** Implement an automated case routing engine that assigns new cases to investigators based on workload, expertise, or round-robin scheduling.

8. **Regulatory Reporting:** Add a scheduled report generator (PDF/CSV) that produces SAR (Suspicious Activity Report) drafts from resolved fraud cases for compliance teams.

---

## 14. References

1. **Ramakrishnan, R. & Gehrke, J.** (2003). *Database Management Systems* (3rd ed.). McGraw-Hill. — Foundational reference for normalization theory (1NF, 2NF, 3NF), relational algebra, and query optimization.

2. **Date, C. J.** (2004). *An Introduction to Database Systems* (8th ed.). Addison-Wesley. — Detailed treatment of relational integrity constraints, foreign keys, and the role of triggers and stored procedures.

3. **MySQL 8.0 Reference Manual** (2024). Oracle Corporation. Retrieved from https://dev.mysql.com/doc/refman/8.0/en/ — Authoritative reference for InnoDB storage engine, `utf8mb4_unicode_ci` collation, CREATE TABLE syntax, trigger and stored procedure DDL, SIGNAL statements, and JSON column type.

4. **Werkzeug Documentation — Password Hashing** (2024). Pallets Projects. Retrieved from https://werkzeug.palletsprojects.com/en/3.0.x/utils/#werkzeug.security.generate_password_hash — Reference for PBKDF2-SHA256 implementation and usage.

5. **Flask Documentation** (2024). Pallets Projects. Retrieved from https://flask.palletsprojects.com/en/3.0.x/ — Reference for Blueprint architecture, session management, `before_request` hooks, and request context.

6. **React Documentation** (2024). Meta Open Source. Retrieved from https://react.dev/ — Reference for React 18 concepts including functional components, hooks, and SPA routing.

7. **Vite Documentation** (2024). Retrieved from https://vitejs.dev/guide/ — Reference for the Vite build tool and dev server configuration used in the frontend.

8. **Recharts Documentation** (2024). Retrieved from https://recharts.org/en-US/ — Reference for BarChart, LineChart, PieChart, and customized visualization components.

9. **pytest Documentation** (2024). Retrieved from https://docs.pytest.org/en/stable/ — Reference for test collection, fixture management, and assertion introspection used in unit and integration tests.

10. **OWASP CSRF Prevention Cheat Sheet** (2024). Open Web Application Security Project. Retrieved from https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html — Guidance for the synchronizer token pattern implemented via `X-CSRF-Token`.

11. **OWASP SQL Injection Prevention Cheat Sheet** (2024). Open Web Application Security Project. Retrieved from https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html — Guidance for parameterized query usage with `%s` placeholders.

12. **Bhattacharyya, S., Jha, S., Tharakunnel, K., & Westland, J. C.** (2011). Data mining for credit card fraud: A comparative study. *Decision Support Systems*, 50(3), 602–613. — Background on rule-based vs. statistical fraud detection approaches.

---

## 15. Appendix Checklist

The following checklist confirms the deliverables included in this project submission.

### A. Database Objects

| Item | Description | Status |
|---|---|---|
| Schema DDL | 9 InnoDB tables with all columns, types, and constraints | ✅ Implemented |
| Normalization | All 9 tables verified to 3NF | ✅ Documented |
| Primary Keys | AUTO_INCREMENT surrogate keys on all 9 tables | ✅ Implemented |
| Unique Constraints | 6 UNIQUE constraints (business keys + 1-to-1 FKs) | ✅ Implemented |
| Foreign Keys | 9 foreign keys with appropriate ON DELETE actions | ✅ Implemented |
| CHECK Constraints | 3 CHECK constraints (amount > 0, score range, points > 0) | ✅ Implemented |
| Secondary Indexes | 13 named indexes across 7 tables | ✅ Implemented |
| View 1 | `v_dashboard_summary` — aggregate KPI view | ✅ Implemented |
| View 2 | `v_case_overview` — case management join view | ✅ Implemented |
| View 3 | `v_merchant_risk` — merchant risk analytics view | ✅ Implemented |
| Trigger 1 | `trg_case_resolved_at` — auto timestamp management | ✅ Implemented |
| Trigger 2 | `trg_audit_logs_no_update` — audit immutability | ✅ Implemented |
| Trigger 3 | `trg_audit_logs_no_delete` — audit immutability | ✅ Implemented |
| Stored Procedure | `sp_update_case_status` — atomic case lifecycle | ✅ Implemented |
| Seed Data | 130 synthetic transactions, 7 cases, 2 users, 5 customers, 10 merchants | ✅ Implemented |

### B. Application

| Item | Description | Status |
|---|---|---|
| Backend | Flask REST API, 21 endpoints, 6 blueprints | ✅ Implemented |
| Fraud Engine | 6-rule scoring engine with per-rule factors, v1.0 | ✅ Implemented |
| Frontend | React 18 + Vite SPA, 8 routes | ✅ Implemented |
| Dashboard | `v_dashboard_summary` KPI cards + trends chart | ✅ Implemented |
| Analytics | Risk distribution, daily volume, merchant risk, hourly heatmap | ✅ Implemented |
| Case Management | Case list, detail, status transitions via stored procedure | ✅ Implemented |
| Admin Panel | Users, customers, merchants, audit log | ✅ Implemented |

### C. Security

| Item | Description | Status |
|---|---|---|
| Password Hashing | Werkzeug PBKDF2-SHA256 | ✅ Implemented |
| Session Auth | Flask sessions + SECRET_KEY from .env | ✅ Implemented |
| CSRF Protection | Token issued at login, validated on all mutating requests | ✅ Implemented |
| Parameterized SQL | All queries use %s placeholders | ✅ Implemented |
| Role-Based Access | Admin vs. investigator; enforced in API and stored procedure | ✅ Implemented |
| Secrets in .env | `.env` excluded from git via `.gitignore` | ✅ Implemented |

### D. Testing

| Item | Description | Status |
|---|---|---|
| Unit tests | 10 tests covering all 6 rules + auth + edge cases | ✅ 10/10 PASSED |
| Integration tests | 6 tests covering health, auth, assessment, SP, triggers, e2e workflow | ✅ 6/6 PASSED |
| **Total** | **16 tests** | ✅ **16/16 PASSED** |

### E. Documentation

| Item | Description | Status |
|---|---|---|
| Academic Report | Full report with all 15 sections | ✅ This document |
| Data Dictionary | All 9 tables documented | ✅ Section 7 |
| Worked Example | Synthetic scoring example with all 6 rules | ✅ Section 9.5 |
| API Reference | All 21 endpoints documented | ✅ Section 10.2 |
| Normalization | 1NF, 2NF, 3NF with schema evidence | ✅ Section 6.2 |

---

*End of Report*

---

> **Student Declaration:** I hereby declare that this project and report are my own work. All external references have been cited. The code and documentation were produced for the BCSE302L — Database Systems course at Vellore Institute of Technology, Vellore.
>
> **Name:** Pandilla S Akhila | **Register Number:** 24BCE1240 | **Course:** BCSE302L
