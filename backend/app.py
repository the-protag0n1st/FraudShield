import os
import sys
import logging
from decimal import Decimal
from datetime import datetime, date
from flask import Flask, jsonify, request, session
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import Config
from backend.auth import validate_csrf
from backend.routes.auth import auth_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.transactions import transactions_bp
from backend.routes.cases import cases_bp
from backend.routes.analytics import analytics_bp
from backend.routes.admin import admin_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fraudshield")

class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON serializer handling Decimal, datetime, and date cleanly."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json = CustomJSONProvider(app)

    # Configure CORS with credentials support for React frontend
    CORS(
        app,
        origins=[config_class.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
        supports_credentials=True,
        allow_headers=["Content-Type", "X-CSRF-Token", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    # CSRF Protection Hook for state-changing requests
    @app.before_request
    def check_csrf_protection():
        # Exempt safe methods and login/health endpoints from CSRF check
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return None
        if request.path in ("/api/auth/login", "/api/health"):
            return None
        
        # Verify CSRF token
        if not validate_csrf():
            logger.warning(f"CSRF validation failed for {request.method} {request.path}")
            return jsonify({
                "error": "Invalid or missing CSRF token. Please refresh the page.",
                "code": "CSRF_ERROR"
            }), 403

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        from backend.db import query_one
        try:
            db_res = query_one("SELECT 1 AS ok")
            db_status = "connected" if db_res and db_res.get("ok") == 1 else "unresponsive"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return jsonify({
            "status": "healthy",
            "service": "FraudShield Backend API",
            "database": db_status,
            "version": "1.0.0"
        })

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"error": "Requested resource not found.", "code": "NOT_FOUND"}), 404

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({"error": str(e.description) if hasattr(e, "description") else "Bad request.", "code": "BAD_REQUEST"}), 400

    @app.errorhandler(Exception)
    def handle_server_error(e):
        logger.error(f"Unhandled server error: {e}", exc_info=True)
        return jsonify({
            "error": "An internal server error occurred. Please contact the administrator.",
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_DEBUG)
