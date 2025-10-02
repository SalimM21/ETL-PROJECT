CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

-- Raw landing of each extract (one row per file)
CREATE TABLE IF NOT EXISTS staging.videos_raw (
  id BIGSERIAL PRIMARY KEY,
  captured_at TIMESTAMPTZ NOT NULL,
  channel_id TEXT NOT NULL,
  payload JSONB NOT NULL
);

-- Flattened (one row per video per capture)
CREATE TABLE IF NOT EXISTS staging.videos_flat (
  captured_at TIMESTAMPTZ NOT NULL,
  video_id TEXT NOT NULL,
  title TEXT,
  published_at TIMESTAMPTZ,
  duration_iso TEXT,
  duration_seconds INT,
  view_count BIGINT,
  like_count BIGINT,
  comment_count BIGINT,
  PRIMARY KEY (captured_at, video_id)
);

-- Core
CREATE TABLE IF NOT EXISTS core.dim_video (
  video_id TEXT PRIMARY KEY,
  title TEXT,
  first_published_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS core.fact_video_metrics (
  captured_at TIMESTAMPTZ NOT NULL,
  video_id TEXT NOT NULL,
  view_count BIGINT,
  like_count BIGINT,
  comment_count BIGINT,
  duration_seconds INT,
  PRIMARY KEY (captured_at, video_id),
  FOREIGN KEY (video_id) REFERENCES core.dim_video(video_id)
);
