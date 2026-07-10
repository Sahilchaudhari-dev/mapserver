import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.config import settings

# Connection pool — created once when app starts
# reuses existing connections instead of opening new ones each time
connection_pool = pool.SimpleConnectionPool(
    minconn=1,   # minimum connections to keep open
    maxconn=10,  # maximum connections allowed
    host=settings.db_host,
    port=settings.db_port,
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    cursor_factory=RealDictCursor
)

def get_connection():
    # gets an existing connection from pool instead of opening new one
    return connection_pool.getconn()

def release_connection(conn):
    # returns connection back to pool for reuse
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
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            release_connection(conn)  # always returns to pool even if error