DROP VIEW all_tags;

CREATE VIEW all_tags (tag, resource_type, count) AS
WITH tags AS (
  SELECT unnest(tags) AS tag, 'songs' AS resource_type FROM songs
  UNION ALL
  SELECT unnest(tags) AS tag, 'song_versions' AS resource_type FROM song_versions
  UNION ALL
  SELECT unnest(tags) AS tag, 'song_sheets' AS resource_type FROM song_sheets
  UNION ALL
  SELECT unnest(tags) AS tag, 'song_media' AS resource_type FROM song_media
  UNION ALL
  SELECT unnest(tags) AS tag, 'setlists' AS resource_type FROM setlists
  UNION ALL
  SELECT unnest(tags) AS tag, 'setlist_templates' AS resource_type FROM setlist_templates
)
SELECT tag, resource_type, count(*) AS count FROM tags
GROUP BY tag, resource_type
ORDER BY tag, resource_type;

UPDATE _version SET ver = 7 WHERE pk = 'db_version';
