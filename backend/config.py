import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "fraudshield_db")
    DB_TEST_NAME = os.getenv("DB_TEST_NAME", "fraudshield_test")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-fraudshield-2026-secure")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    
    # Session cookie security settings
    SESSION_COOKIE_NAME = "fraudshield_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Configurable Fraud Engine Thresholds
    FRAUD_AMOUNT_THRESHOLD = float(os.getenv("FRAUD_AMOUNT_THRESHOLD", "5000.00"))
    FRAUD_VELOCITY_COUNT = int(os.getenv("FRAUD_VELOCITY_COUNT", "3"))
    FRAUD_AVG_MULTIPLIER = float(os.getenv("FRAUD_AVG_MULTIPLIER", "3.0"))
    FRAUD_MIN_HISTORY_COUNT = int(os.getenv("FRAUD_MIN_HISTORY_COUNT", "3"))
    FRAUD_FAILED_COUNT = int(os.getenv("FRAUD_FAILED_COUNT", "2"))
