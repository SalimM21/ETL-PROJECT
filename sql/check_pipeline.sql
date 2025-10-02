-- docker exec -it elt-project_5e4bbe-postgres-1 psql -U postgres -d postgres
\dn
-- 1. Vérifier les tables dans chaque schéma
\dt staging.*
\dt core.*

-- 2. Vérifier le contenu brut (JSON par fichier)
SELECT id, captured_at, channel_id, left(payload::text, 200) AS payload_preview
FROM staging.videos_raw
ORDER BY captured_at DESC
LIMIT 5;

-- 3. Vérifier les vidéos aplaties
SELECT captured_at, video_id, title, view_count, like_count, comment_count
FROM staging.videos_flat
ORDER BY captured_at DESC
LIMIT 10;

-- 4. Vérifier la dimension vidéo
SELECT video_id, title, first_published_at
FROM core.dim_video
ORDER BY first_published_at DESC
LIMIT 10;

-- 5. Vérifier la table des faits (métriques)
SELECT captured_at, video_id, view_count, like_count, comment_count, duration_seconds
FROM core.fact_video_metrics
ORDER BY captured_at DESC
LIMIT 10;
