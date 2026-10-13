CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE song_versions ADD COLUMN lyrics_embedding vector(384);

DROP TRIGGER revision_track_song_versions ON song_versions;
CREATE TRIGGER revision_track_song_versions
BEFORE UPDATE OF label, verse_order, lyrics, tags OR DELETE ON song_versions
FOR EACH ROW
EXECUTE FUNCTION revision_track_song_versions();

UPDATE _version SET ver = 9 WHERE pk = 'db_version';
