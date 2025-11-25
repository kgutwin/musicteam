ALTER TABLE song_versions
ADD COLUMN lyrics_tsv TSVECTOR
GENERATED ALWAYS AS (to_tsvector('english', coalesce(lyrics, ''))) STORED;

CREATE INDEX lyrics_idx ON song_versions USING gin (lyrics_tsv);

UPDATE _version SET ver = 4 WHERE pk = 'db_version';
