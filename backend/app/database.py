import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.config import settings

connection_pool = pool.SimpleConnectionPool(
    minconn=1,   
    maxconn=10,
    host=settings.db_host,
    port=settings.db_port,
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    cursor_factory=RealDictCursor
)

def get_connection():
     return connection_pool.getconn()

def release_connection(conn):
       connection_pool.putconn(conn)

def test_connection():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT postgis_version();")
        result = cur.fetchone()
        cur.close()
        return result
    except Exception:
        logger.exception("Database connection test failed")
        raise
    finally:
        if conn:
            release_connection(conn)