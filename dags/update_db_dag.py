import json, glob
from datetime import datetime, timedelta
from isodate import parse_duration
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
import psycopg2

RAW_DIR = "/usr/local/airflow/include/data/raw"

def _get_conn():
    conn = BaseHook.get_connection("postgres_default")
    host = conn.host or "postgres"
    if host in ("localhost","127.0.0.1"):  # inside container, use service name
        host = "postgres"
    try:
        return psycopg2.connect(
            host=host, port=conn.port or 5432,
            dbname=conn.schema or "postgres",
            user=conn.login or "postgres",
            password=conn.password or "postgres"
        )
    except Exception as e:
        raise AirflowException(f"Postgres connection failed: {e}")

def ensure_tables():
    with _get_conn() as c, c.cursor() as cur:
        with open("/usr/local/airflow/sql/staging_core.sql","r",encoding="utf-8") as f:
            cur.execute(f.read())

def load_latest_json():
    files = sorted(glob.glob(f"{RAW_DIR}/*.json"))
    if not files:
        raise AirflowException("No JSON files found. Run produce_JSON first.")
    latest = files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support BOTH shapes:
    # A) new: {"videos":[{title,...}] , "extraction_date": "..."}
    # B) old: {"items":[{id, snippet, contentDetails, statistics}], "captured_at": "..."}
    if "videos" in data:
        captured_at = data.get("extraction_date")
        items = data.get("videos", [])
        use_flat = True
    elif "items" in data:
        captured_at = data.get("captured_at")
        items = data.get("items", [])
        use_flat = False
    else:
        raise AirflowException("Unknown JSON structure: neither 'videos' nor 'items' present.")

    if not captured_at:
        raise AirflowException("Missing timestamp (extraction_date/captured_at) in JSON.")

    with _get_conn() as c, c.cursor() as cur:
        # raw landing (store the original list only)
        cur.execute(
            "INSERT INTO staging.videos_raw (captured_at, channel_id, payload) VALUES (%s,%s,%s)",
            (captured_at, data.get("channel_handle") or data.get("channel_id"), json.dumps(items))
        )

        if use_flat:
            # New flat structure from our extractor
            for it in items:
                vid = it.get("video_id")
                title = it.get("title")
                published_at = it.get("published_at")
                dur_iso = it.get("duration")
                dur_s = int(parse_duration(dur_iso).total_seconds()) if dur_iso else None
                vc = it.get("view_count"); lc = it.get("like_count"); cc = it.get("comment_count")

                cur.execute("""
                    INSERT INTO staging.videos_flat
                    (captured_at, video_id, title, published_at, duration_iso, duration_seconds, view_count, like_count, comment_count)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (captured_at, video_id) DO NOTHING
                """, (captured_at, vid, title, published_at, dur_iso, dur_s, vc, lc, cc))
        else:
            # Old structure coming straight from YouTube API
            for it in items:
                vid = it.get("id") or (it.get("id") or {})
                if isinstance(vid, dict):
                    vid = vid.get("videoId")
                if not vid:
                    continue
                snip = it.get("snippet", {})
                stats = it.get("statistics", {})
                cont  = it.get("contentDetails", {})
                title = snip.get("title")
                published_at = snip.get("publishedAt")
                dur_iso = cont.get("duration")
                dur_s = int(parse_duration(dur_iso).total_seconds()) if dur_iso else None
                vc = int(stats.get("viewCount", 0)) if stats.get("viewCount") else None
                lc = int(stats.get("likeCount", 0)) if stats.get("likeCount") else None
                cc = int(stats.get("commentCount", 0)) if stats.get("commentCount") else None

                cur.execute("""
                    INSERT INTO staging.videos_flat
                    (captured_at, video_id, title, published_at, duration_iso, duration_seconds, view_count, like_count, comment_count)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (captured_at, video_id) DO NOTHING
                """, (captured_at, vid, title, published_at, dur_iso, dur_s, vc, lc, cc))

        # core dim upsert + fact append
        cur.execute("""
            INSERT INTO core.dim_video (video_id, title, first_published_at)
            SELECT DISTINCT video_id, title, published_at
            FROM staging.videos_flat
            ON CONFLICT (video_id) DO NOTHING
        """)
        cur.execute("""
            INSERT INTO core.fact_video_metrics (captured_at, video_id, view_count, like_count, comment_count, duration_seconds)
            SELECT captured_at, video_id, view_count, like_count, comment_count, duration_seconds
            FROM staging.videos_flat
            WHERE captured_at = %s
            ON CONFLICT (captured_at, video_id) DO NOTHING
        """, (captured_at,))

def pipeline():
    ensure_tables()
    load_latest_json()

default_args = {"owner": "you", "retries": 1, "retry_delay": timedelta(minutes=2)}

with DAG(
    dag_id="update_db",
    start_date=datetime(2025, 9, 15),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["youtube","load","transform"],
):
    t = PythonOperator(task_id="ensure_and_load", python_callable=pipeline)
