CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE song_versions ADD COLUMN lyrics_embedding vector(384);

UPDATE _version SET ver = 9 WHERE pk = 'db_version';
