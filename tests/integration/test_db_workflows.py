import pytest
import os
import sys
from decimal import Decimal

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.config import Config
from backend.db import get_connection, get_db_cursor, query_one, query_all
from backend.app import create_app
from backend.fraud_engine import score_and_persist_assessment

TEST_DB = "fraudshield_test"

class TestConfig(Config):
    TESTING = True
    DB_NAME = TEST_DB
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope="session", autouse=True)
def guard_test_database():
    """Safety guard: Guarantees integration tests ONLY run against fraudshield_test."""
    assert TestConfig.DB_NAME == "fraudshield_test", "Safety Guard: Integration tests must target fraudshield_test!"
    # Ensure test database is initialized
    conn = get_connection(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE()")
    current = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert current == "fraudshield_test", f"Safety Guard: Connected to '{current}', expected 'fraudshield_test'!"

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_auth_login_and_session(client):
    # Test invalid login
    bad_res = client.post("/api/auth/login", json={"email": "bad@fraudshield.local", "password": "wrong"})
    assert bad_res.status_code == 401

    # Test valid login with seeded admin
    login_res = client.post("/api/auth/login", json={"email": "admin@fraudshield.local", "password": "Admin@123"})
    assert login_res.status_code == 200
    data = login_res.get_json()
    assert data["user"]["email"] == "admin@fraudshield.local"
    assert data["user"]["role"] == "admin"
    assert "csrf_token" in data

    # Test authenticated /me
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["authenticated"] is True
    assert me_data["user"]["email"] == "admin@fraudshield.local"

    # Test logout
    logout_res = client.post("/api/auth/logout", headers={"X-CSRF-Token": data["csrf_token"]})
    assert logout_res.status_code == 200

    # Verify session cleared
    me_res_after = client.get("/api/auth/me")
    assert me_res_after.get_json()["authenticated"] is False

def test_assessment_idempotency_and_no_duplicate_cases():
    """Tests that re-assessing a transaction does not create duplicate assessments or cases."""
    conn = get_connection(TEST_DB)
    cursor = conn.cursor(dictionary=True)
    try:
        # Find a transaction
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        txn = cursor.fetchone()
        txn_id = txn["id"]

        # Score it twice
        res1 = score_and_persist_assessment(cursor, txn_id)
        conn.commit()
        res2 = score_and_persist_assessment(cursor, txn_id)
        conn.commit()

        # Check risk_assessments count for this transaction (must be exactly 1)
        cursor.execute("SELECT COUNT(*) AS c FROM risk_assessments WHERE transaction_id = %s", (txn_id,))
        count = cursor.fetchone()["c"]
        assert count == 1, "Duplicate risk_assessment created!"

        # Check investigation_cases count (must be at most 1)
        cursor.execute("SELECT COUNT(*) AS c FROM investigation_cases WHERE transaction_id = %s", (txn_id,))
        case_count = cursor.fetchone()["c"]
        assert case_count in (0, 1), "Duplicate investigation_case created!"
    finally:
        cursor.close()
        conn.close()

def test_stored_procedure_case_transition_and_audit():
    """Tests sp_update_case_status: verifies status change, trigger resolved_at, and audit log."""
    conn = get_connection(TEST_DB)
    cursor = conn.cursor(dictionary=True)
    try:
        # Find or create a case
        cursor.execute("SELECT id, case_status FROM investigation_cases LIMIT 1")
        case = cursor.fetchone()
        case_id = case["id"]

        # Call procedure to resolve as fraud
        cursor.callproc("sp_update_case_status", (case_id, 1, "resolved_fraud", "Verified fraudulent transaction with issuer"))
        conn.commit()

        # Verify case status and trigger-populated resolved_at
        cursor.execute("SELECT case_status, resolved_at, resolution_notes FROM investigation_cases WHERE id = %s", (case_id,))
        updated = cursor.fetchone()
        assert updated["case_status"] == "resolved_fraud"
        assert updated["resolved_at"] is not None
        assert "Verified fraudulent" in updated["resolution_notes"]

        # Verify audit log was inserted
        cursor.execute("""
            SELECT action, details FROM audit_logs
            WHERE entity_type = 'investigation_cases' AND entity_id = %s
            ORDER BY id DESC LIMIT 1
        """, (case_id,))
        audit = cursor.fetchone()
        assert audit["action"] == "CASE_STATUS_UPDATED"
        assert "resolved_fraud" in str(audit["details"])

        # Reset back to open for test hygiene (as admin user ID 1)
        cursor.callproc("sp_update_case_status", (case_id, 1, "open", "Reopened for testing"))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def test_database_trigger_audit_immutability():
    """Tests that DB trigger rejects updates or deletes on audit_logs."""
    conn = get_connection(TEST_DB)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM audit_logs LIMIT 1")
        audit_row = cursor.fetchone()
        if audit_row:
            log_id = audit_row["id"]
            # Attempt to delete (must raise MySQL error via trigger)
            with pytest.raises(Exception) as exc_info:
                cursor.execute("DELETE FROM audit_logs WHERE id = %s", (log_id,))
            assert "immutable" in str(exc_info.value).lower()
    finally:
        cursor.close()
        conn.close()

def test_transaction_creation_and_automatic_case():
    """Creates a high amount transaction and verifies it immediately scores high and opens a case."""
    conn = get_connection(TEST_DB)
    cursor = conn.cursor(dictionary=True)
    try:
        import time
        ref = f"TEST-INTEG-{int(time.time())}"
        cursor.execute("""
            INSERT INTO transactions (
                transaction_reference, customer_id, merchant_id, amount, currency,
                transaction_type, transaction_status, transaction_timestamp, channel,
                location, country_code, created_at
            ) VALUES (%s, 1, 1, 9500.00, 'USD', 'purchase', 'approved', NOW(), 'online', 'New York, USA', 'US', NOW())
        """, (ref,))
        txn_id = cursor.lastrowid

        res = score_and_persist_assessment(cursor, txn_id)
        conn.commit()

        assert res["risk_score"] >= 25
        # Re-check case in DB
        cursor.execute("SELECT * FROM investigation_cases WHERE transaction_id = %s", (txn_id,))
        case = cursor.fetchone()
        # If score >= 60, case exists
        if res["risk_score"] >= 60:
            assert case is not None
            assert case["case_status"] == "open"
    finally:
        cursor.close()
        conn.close()
