import psycopg2
import pandas as pd
import os

def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "postgres"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
    )

def fetch_videos(limit=20):
    query = """
        SELECT f.captured_at, d.title, d.video_id,
               f.view_count, f.like_count, f.comment_count, f.duration_seconds
        FROM core.fact_video_metrics f
        JOIN core.dim_video d ON f.video_id = d.video_id
        ORDER BY f.captured_at DESC
        LIMIT %s;
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=(limit,))
