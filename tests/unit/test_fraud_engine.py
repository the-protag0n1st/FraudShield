import pytest
from decimal import Decimal
from backend.fraud_engine import evaluate_rules, determine_risk_level

def test_risk_level_boundaries():
    assert determine_risk_level(0) == "low"
    assert determine_risk_level(29) == "low"
    assert determine_risk_level(30) == "medium"
    assert determine_risk_level(59) == "medium"
    assert determine_risk_level(60) == "high"
    assert determine_risk_level(79) == "high"
    assert determine_risk_level(80) == "critical"
    assert determine_risk_level(100) == "critical"

def test_rule_a_high_amount():
    txn = {"amount": 7500.00, "country_code": "US", "merchant_id": 1}
    history = {"prior_count": 0, "recent_10m_count": 0, "recent_failed_count": 0}
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 25
    assert res["risk_level"] == "low"
    assert any(f["rule_code"] == "RULE_A_HIGH_AMOUNT" for f in res["factors"])

def test_rule_b_velocity_burst():
    txn = {"amount": 100.00, "country_code": "US", "merchant_id": 1}
    history = {"prior_count": 5, "recent_10m_count": 3, "recent_failed_count": 0, "prior_with_this_merchant": 2}
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 20
    assert any(f["rule_code"] == "RULE_B_HIGH_VELOCITY" for f in res["factors"])

def test_rule_c_amount_spike():
    txn = {"amount": 1500.00, "country_code": "US", "merchant_id": 1}
    # Customer avg is 300, 1500 is 5x avg (>= 3.0x multiplier)
    history = {
        "prior_count": 5,
        "prior_avg_amount": Decimal("300.00"),
        "prior_with_this_merchant": 2,
        "recent_10m_count": 0,
        "recent_failed_count": 0
    }
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 20
    assert any(f["rule_code"] == "RULE_C_AMOUNT_SPIKE" for f in res["factors"])

def test_rule_c_skips_when_insufficient_history():
    txn = {"amount": 1500.00, "country_code": "US", "merchant_id": 1}
    # Only 1 prior transaction
    history = {
        "prior_count": 1,
        "prior_avg_amount": Decimal("100.00"),
        "recent_10m_count": 0,
        "recent_failed_count": 0
    }
    res = evaluate_rules(txn, history)
    assert not any(f["rule_code"] == "RULE_C_AMOUNT_SPIKE" for f in res["factors"])

def test_rule_d_failed_attempts():
    txn = {"amount": 250.00, "country_code": "US", "merchant_id": 1}
    history = {"prior_count": 2, "recent_failed_count": 2, "recent_10m_count": 0}
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 15
    assert any(f["rule_code"] == "RULE_D_FAILED_ATTEMPTS" for f in res["factors"])

def test_rule_e_novel_merchant():
    txn = {"amount": 150.00, "merchant_name": "Apex Electronics", "country_code": "US", "merchant_id": 9}
    history = {
        "prior_count": 6,
        "prior_avg_amount": Decimal("200.00"),
        "prior_with_this_merchant": 0,  # Never seen
        "recent_10m_count": 0,
        "recent_failed_count": 0
    }
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 10
    assert any(f["rule_code"] == "RULE_E_NEW_MERCHANT" for f in res["factors"])

def test_rule_f_location_mismatch():
    txn = {"amount": 100.00, "country_code": "FR", "merchant_id": 1}
    history = {
        "prior_count": 4,
        "prior_with_this_merchant": 2,
        "recent_10m_count": 0,
        "recent_failed_count": 0,
        "last_recent_country": "US"  # Mismatch within 60 mins
    }
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 20
    assert any(f["rule_code"] == "RULE_F_LOCATION_MISMATCH" for f in res["factors"])

def test_critical_combo_capped_at_100():
    # All rules trigger: 25 + 20 + 20 + 15 + 10 + 20 = 110 points -> capped at 100
    txn = {"amount": 8000.00, "merchant_name": "CryptoExchange X", "country_code": "UK", "merchant_id": 99}
    history = {
        "prior_count": 10,
        "prior_avg_amount": Decimal("500.00"),
        "prior_with_this_merchant": 0,
        "recent_10m_count": 4,
        "recent_failed_count": 3,
        "last_recent_country": "US"
    }
    res = evaluate_rules(txn, history)
    assert res["risk_score"] == 100
    assert res["risk_level"] == "critical"
    assert res["is_flagged"] is True
    assert len(res["factors"]) == 6
