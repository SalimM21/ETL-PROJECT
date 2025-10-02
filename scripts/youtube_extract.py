import os, json, time, pathlib, requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
from airflow.models import Variable
from airflow.exceptions import AirflowException
import isodate

# Where raw JSON files are stored inside the Airflow container
BASE_DIR = "/usr/local/airflow/include/data/raw"
pathlib.Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

# ---------- helpers ----------

def _duration_readable(duration_iso: str) -> str:
    """Convert ISO8601 duration 'PT37M4S' -> '37:04' or 'H:MM:SS' when hours > 0."""
    if not duration_iso:
        return ""
    total = int(isodate.parse_duration(duration_iso).total_seconds())
    m, s = divmod(total, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def _req(url: str, params: Dict) -> Dict:
    r = requests.get(url, params=params, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise AirflowException(f"HTTP {r.status_code}: {e} - {r.text[:400]}")
    return r.json()

# ---------- YouTube calls ----------

def fetch_video_ids(api_key: str, channel_id: str, published_after: Optional[str], max_pages: int) -> List[str]:
    """List recent video IDs via search endpoint."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": channel_id,
        "part": "id",
        "order": "date",
        "maxResults": 50,
        "type": "video",
    }
    if published_after:
        params["publishedAfter"] = published_after

    ids, page = [], 0
    while True:
        page += 1
        data = _req(url, params)
        ids += [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]
        token = data.get("nextPageToken")
        if not token or page >= max_pages:
            break
        params["pageToken"] = token
        time.sleep(0.15)
    return ids

def fetch_video_details(api_key: str, video_ids: List[str]) -> List[Dict]:
    """Get snippet, contentDetails, statistics for a list of video IDs."""
    url = "https://www.googleapis.com/youtube/v3/videos"
    out: List[Dict] = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        params = {
            "key": api_key,
            "id": ",".join(chunk),
            "part": "snippet,contentDetails,statistics",
            "maxResults": 50
        }
        data = _req(url, params)
        out.extend(data.get("items", []))
        time.sleep(0.15)
    return out

# ---------- main callable for Airflow ----------

def run_extract(**context):
    # Prefer Airflow Variables; fall back to env if present
    api_key = Variable.get("YOUTUBE_API_KEY", default_var=os.getenv("YOUTUBE_API_KEY"))
    if not api_key:
        raise AirflowException("Missing YOUTUBE_API_KEY (Airflow Variable or env).")
    channel_id = Variable.get("CHANNEL_ID", default_var=os.getenv("CHANNEL_ID", "UCX6OQ3DkcsbYNE6H8uQQuVA"))
    channel_handle = Variable.get("CHANNEL_HANDLE", default_var=os.getenv("CHANNEL_HANDLE", "MrBeast"))

    # Keep it light for now (you can increase to 5–10 later)
    video_ids = fetch_video_ids(api_key, channel_id, published_after=None, max_pages=1)
    details = fetch_video_details(api_key, video_ids) if video_ids else []

    # Transform to your exact target JSON shape
    videos_out: List[Dict] = []
    for it in details:
        stats = it.get("statistics", {})
        snip  = it.get("snippet", {})
        cont  = it.get("contentDetails", {})

        duration_iso = cont.get("duration")
        videos_out.append({
            "title": snip.get("title"),
            "duration": duration_iso,
            "duration_readable": _duration_readable(duration_iso),
            "video_id": it.get("id"),
            "view_count": int(stats.get("viewCount", 0)) if stats.get("viewCount") is not None else 0,
            "like_count": int(stats.get("likeCount", 0)) if stats.get("likeCount") is not None else 0,
            "comment_count": int(stats.get("commentCount", 0)) if stats.get("commentCount") is not None else 0,
            "published_at": snip.get("publishedAt"),
        })

    payload = {
        "channel_handle": channel_handle,
        "extraction_date": datetime.now(timezone.utc).isoformat(),
        "total_videos": len(videos_out),
        "videos": videos_out
    }

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_handle = "".join(ch for ch in channel_handle if ch.isalnum() or ch in ("-", "_"))
    out_path = f"{BASE_DIR}/{safe_handle}_videos_{ts}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote file: {out_path}")
    print(f"   total_videos: {payload['total_videos']}")
    return out_path
