import secrets
from functools import wraps
from flask import session, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.db import query_one

def hash_password(password: str) -> str:
    """Hashes a plaintext password using Werkzeug pbkdf2:sha256."""
    return generate_password_hash(password, method="pbkdf2:sha256")

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a plaintext password against the stored Werkzeug hash."""
    return check_password_hash(stored_hash, password)

def get_csrf_token() -> str:
    """Retrieves or creates a per-session CSRF token."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

def validate_csrf():
    """
    Validates CSRF token for state-changing HTTP requests.
    Exempts safe methods (GET, HEAD, OPTIONS).
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return True
    
    # Check origin/referer header match if present
    # Check CSRF token from header
    token = request.headers.get("X-CSRF-Token")
    expected_token = session.get("_csrf_token")
    
    if not token or not expected_token or not secrets.compare_digest(token, expected_token):
        return False
    return True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required", "code": "UNAUTHORIZED"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required", "code": "UNAUTHORIZED"}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "Administrator privileges required", "code": "FORBIDDEN"}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Fetches full active user record for current session."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return query_one(
        "SELECT id, full_name, email, role, is_active, created_at FROM users WHERE id = %s AND is_active = TRUE",
        (user_id,)
    )
