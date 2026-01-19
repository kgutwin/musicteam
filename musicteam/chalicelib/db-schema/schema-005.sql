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
            rev_created_on,
            rev_changed_by,
            id, title, authors, ccli_num, tags
        ) VALUES (
            coalesce(NEW.last_modified, OLD.last_modified),
            current_setting('my.id', TRUE),
            OLD.id, OLD.title, OLD.authors, OLD.ccli_num, OLD.tags
        );
        NEW.last_modified = localtimestamp(4);
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER revision_track_songs BEFORE UPDATE OR DELETE ON songs
FOR EACH ROW
EXECUTE FUNCTION revision_track_songs();

ALTER TABLE song_versions
ADD COLUMN last_modified TIMESTAMP DEFAULT (localtimestamp(4));

CREATE TABLE rev_song_versions (
    rev_id TEXT UNIQUE DEFAULT ('rsv:' || uuid_generate_v4()),
    rev_created_on TIMESTAMP,
    rev_changed_by TEXT,
    id TEXT NOT NULL,
    song_id TEXT NOT NULL,
    label TEXT NOT NULL,
    verse_order TEXT,
    lyrics TEXT,
    tags TEXT[],
    PRIMARY KEY (rev_id),
    FOREIGN KEY (rev_changed_by) REFERENCES users (id)
);

CREATE FUNCTION revision_track_song_versions() RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO rev_song_versions (
            rev_created_on,
            rev_changed_by,
            id, song_id, label, verse_order, lyrics, tags
        ) VALUES (
            coalesce(NEW.last_modified, OLD.last_modified),
            current_setting('my.id', TRUE),
            OLD.id, OLD.song_id, OLD.label, OLD.verse_order, OLD.lyrics, OLD.tags
        );
        NEW.last_modified = localtimestamp(4);
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER revision_track_song_versions BEFORE UPDATE OR DELETE ON song_versions
FOR EACH ROW
EXECUTE FUNCTION revision_track_song_versions();

ALTER TABLE song_sheets ADD COLUMN last_modified TIMESTAMP DEFAULT (localtimestamp(4));

CREATE TABLE rev_song_sheets (
    rev_id TEXT UNIQUE DEFAULT ('rss:' || uuid_generate_v4()),
    rev_created_on TIMESTAMP,
    rev_changed_by TEXT,
    id TEXT NOT NULL,
    song_id TEXT NOT NULL,
    song_version_id TEXT NOT NULL,
    type TEXT NOT NULL,
    key TEXT NOT NULL,
    tags TEXT[],
    object_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    PRIMARY KEY (rev_id),
    FOREIGN KEY (rev_changed_by) REFERENCES users (id)
);

CREATE FUNCTION revision_track_song_sheets() RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO rev_song_sheets(
            rev_created_on,
            rev_changed_by,
            id, song_id, song_version_id, type, key, tags, object_id, object_type
        ) VALUES (
            coalesce(NEW.last_modified, OLD.last_modified),
            current_setting('my.id', TRUE),
            OLD.id,
            (SELECT song_id FROM song_versions WHERE id = OLD.song_version_id),
            OLD.song_version_id, OLD.type, OLD.key, OLD.tags, OLD.object_id,
            OLD.object_type
        );
        NEW.last_modified = localtimestamp(4);
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER revision_track_song_sheets BEFORE UPDATE OR DELETE ON song_sheets
FOR EACH ROW
EXECUTE FUNCTION revision_track_song_sheets();

UPDATE _version SET ver = 5 WHERE pk = 'db_version';
