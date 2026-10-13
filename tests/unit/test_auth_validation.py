import pytest
from backend.auth import hash_password, verify_password

def test_password_hashing():
    raw_pass = "TestPassword@123"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert hashed.startswith("pbkdf2:sha256:")
    assert verify_password(hashed, raw_pass) is True
    assert verify_password(hashed, "WrongPassword") is False
    assert verify_password(hashed, "") is False
