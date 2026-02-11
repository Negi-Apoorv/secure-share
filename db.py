import mysql.connector
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

def get_db_connection():
    """Create and return a new database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        autocommit=False,
        charset="utf8mb4",
        collation="utf8mb4_bin"
    )

@contextmanager
def db_cursor(dictionary=True):
    """Context manager for database cursor"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()