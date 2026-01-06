ALTER TABLE songs ADD COLUMN last_modified TIMESTAMP DEFAULT (localtimestamp(4));

CREATE TABLE rev_songs (
    rev_id TEXT UNIQUE DEFAULT ('rs:' || uuid_generate_v4()),
    rev_created_on TIMESTAMP,
    rev_changed_by TEXT,
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    authors TEXT[],
    ccli_num INTEGER,
    tags TEXT[],
    PRIMARY KEY (rev_id),
    FOREIGN KEY (rev_changed_by) REFERENCES users (id)
);

CREATE FUNCTION revision_track_songs() RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO rev_songs (
            rev_created_on, rev_changed_by,
            id, title, authors, ccli_num, tags
        ) VALUES (
            NEW.last_modified, current_setting('my.id', TRUE),
            OLD.id, OLD.title, OLD.authors, OLD.ccli_num, OLD.tags
        );
        NEW.last_modified = localtimestamp(4);
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER revision_track_songs BEFORE UPDATE OR DELETE ON songs
FOR EACH ROW
EXECUTE FUNCTION revision_track_songs();

UPDATE _version SET ver = 5 WHERE pk = 'db_version';
