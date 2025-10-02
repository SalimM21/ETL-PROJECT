CREATE INDEX IF NOT EXISTS ix_staging_videos_flat_vid ON staging.videos_flat (video_id);
CREATE INDEX IF NOT EXISTS ix_staging_videos_flat_captured ON staging.videos_flat (captured_at);
CREATE INDEX IF NOT EXISTS ix_core_fact_vid ON core.fact_video_metrics (video_id);
CREATE INDEX IF NOT EXISTS ix_core_fact_captured ON core.fact_video_metrics (captured_at);
