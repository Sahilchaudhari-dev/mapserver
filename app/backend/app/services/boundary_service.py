from app.database import get_connection, release_connection

def fetch_india_boundary():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT ST_AsGeoJSON(wkb_geometry)::json as geometry, source
            FROM india_boundaries
            LIMIT 1
        """)
        result = cur.fetchone()
        cur.close()

        if result is None:
            return None

        return {
            "type": "Feature",
            "geometry": result["geometry"],
            "properties": {"source": result["source"]}
        }

    except Exception as e:
        raise Exception(f"Database error: {str(e)}")

    finally:
        if conn:
            release_connection(conn)