from flask import Blueprint, request, jsonify, session
from backend.auth import verify_password, get_csrf_token, get_current_user, login_required
from backend.db import query_one, execute_write

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required.", "code": "VALIDATION_ERROR"}), 400

    user = query_one(
        "SELECT id, full_name, email, password_hash, role, is_active FROM users WHERE email = %s",
        (email,)
    )

    if not user or not user["is_active"] or not verify_password(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password.", "code": "INVALID_CREDENTIALS"}), 401

    # Store user identity in server-side session
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]
    session["email"] = user["email"]
    
    # Generate CSRF token for the session
    csrf_token = get_csrf_token()

    # Log successful login in audit log
    execute_write(
        "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details) VALUES (%s, %s, %s, %s, %s)",
        (user["id"], "USER_LOGIN", "users", user["id"], '{"status": "success"}')
    )

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        },
        "csrf_token": csrf_token
    })

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    user_id = session.get("user_id")
    if user_id:
        execute_write(
            "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details) VALUES (%s, %s, %s, %s, %s)",
            (user_id, "USER_LOGOUT", "users", user_id, '{"status": "success"}')
        )
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@auth_bp.route("/me", methods=["GET"])
def me():
    csrf_token = get_csrf_token()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "authenticated": False,
            "csrf_token": csrf_token
        })

    user = get_current_user()
    if not user:
        session.clear()
        return jsonify({
            "authenticated": False,
            "csrf_token": csrf_token
        })

    return jsonify({
        "authenticated": True,
        "user": user,
        "csrf_token": csrf_token
    })
