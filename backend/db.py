import logging
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling
from backend.config import Config

logger = logging.getLogger(__name__)

_pool = None

def get_pool(database_name=None):
    global _pool
    db_name = database_name or Config.DB_NAME
    
    # If pool already exists for this database, reuse it
    if _pool is not None and getattr(_pool, "_database_name", None) == db_name:
        return _pool

    try:
        pool_name = f"fraudshield_pool_{db_name}"
        _pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=10,
            pool_reset_session=True,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=db_name,
            autocommit=False,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )
        _pool._database_name = db_name
        logger.info(f"Initialized MySQL connection pool for database: {db_name}")
        return _pool
    except mysql.connector.Error as err:
        logger.error(f"Failed to create MySQL connection pool: {err}")
        raise

def get_connection(database_name=None):
    """Acquires a pooled MySQL connection."""
    pool = get_pool(database_name)
    try:
        conn = pool.get_connection()
        return conn
    except mysql.connector.PoolError:
        # Fallback to direct connection if pool exhausted
        logger.warning("Pool exhausted, falling back to direct connection")
        db_name = database_name or Config.DB_NAME
        return mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=db_name,
            autocommit=False,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )

@contextmanager
def get_db_cursor(commit=False, dictionary=True, database_name=None):
    """
    Context manager that yields a cursor and manages the connection lifecycle.
    Automatically rolls back on exception and commits if commit=True.
    """
    conn = get_connection(database_name)
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database operation rolled back due to error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def query_one(sql, params=None, database_name=None):
    """Executes a SELECT query and returns a single row as a dict."""
    with get_db_cursor(commit=False, dictionary=True, database_name=database_name) as cursor:
        cursor.execute(sql, params or ())
        return cursor.fetchone()

def query_all(sql, params=None, database_name=None):
    """Executes a SELECT query and returns all matching rows as a list of dicts."""
    with get_db_cursor(commit=False, dictionary=True, database_name=database_name) as cursor:
        cursor.execute(sql, params or ())
        return cursor.fetchall()

def execute_write(sql, params=None, database_name=None):
    """Executes an INSERT/UPDATE/DELETE query and returns lastrowid and rowcount."""
    with get_db_cursor(commit=True, dictionary=True, database_name=database_name) as cursor:
        cursor.execute(sql, params or ())
        return cursor.lastrowid, cursor.rowcount
