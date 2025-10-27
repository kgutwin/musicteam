CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS _version;
CREATE TABLE _version (pk TEXT PRIMARY KEY, major INT, minor INT, patch INT);
INSERT INTO _version (pk, major, minor, patch)
VALUES ('db_version', 0, 1, 0);

CREATE TABLE IF NOT EXISTS users (
  id TEXT UNIQUE DEFAULT ('u:' || uuid_generate_v4()),
  name TEXT NOT NULL,
  provider_id TEXT UNIQUE NOT NULL,
  email TEXT,
  picture TEXT,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  last_login TIMESTAMP,
  role TEXT,
  api_key TEXT,
  PRIMARY KEY (id)
);

DROP VIEW IF EXISTS all_tags;
DROP VIEW IF EXISTS all_authors;
DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
  id TEXT UNIQUE DEFAULT ('s:' || uuid_generate_v4()),
  title TEXT NOT NULL,
  authors TEXT[],
  ccli_num INTEGER,
  tags TEXT[],
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE VIEW all_tags (tag, count) AS
SELECT
  DISTINCT unnest(tags) AS tag,
  COUNT(*) AS count
FROM songs
GROUP BY tag
ORDER BY tag;

CREATE VIEW all_authors (author, count) AS
SELECT
  DISTINCT unnest(authors) AS author,
  COUNT(*) AS count
FROM songs
GROUP BY author
ORDER BY author;

CREATE TABLE IF NOT EXISTS song_versions (
  id TEXT UNIQUE DEFAULT ('sv:' || uuid_generate_v4()),
  song_id TEXT NOT NULL,
  label TEXT NOT NULL,
  verse_order TEXT,
  lyrics TEXT,
  tags TEXT[],
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS song_sheets (
  id TEXT UNIQUE DEFAULT ('ss:' || uuid_generate_v4()),
  song_version_id TEXT NOT NULL,
  type TEXT NOT NULL,
  key TEXT NOT NULL,
  tags TEXT[],
  object_id TEXT NOT NULL,
  object_type TEXT NOT NULL,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (song_version_id) REFERENCES song_versions (id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS song_media (
  id TEXT UNIQUE DEFAULT ('sm:' || uuid_generate_v4()),
  song_version_id TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT,
  object_id TEXT,
  tags TEXT[],
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (song_version_id) REFERENCES song_versions (id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS setlists (
  id TEXT UNIQUE DEFAULT ('l:' || uuid_generate_v4()),
  leader_name TEXT NOT NULL,
  service_date DATE,
  tags TEXT[],
  music_packet_object_id TEXT,
  lyric_packet_object_id TEXT,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS setlist_positions (
  id TEXT UNIQUE DEFAULT ('lp:' || uuid_generate_v4()),
  setlist_id TEXT NOT NULL,
  index INTEGER NOT NULL,
  label TEXT NOT NULL,
  is_music BOOLEAN,
  presenter TEXT,
  status TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (setlist_id) REFERENCES setlists (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS setlist_sheets (
  id TEXT UNIQUE DEFAULT ('ls:' || uuid_generate_v4()),
  setlist_id TEXT NOT NULL,
  type TEXT NOT NULL,
  song_sheet_id TEXT NOT NULL,
  setlist_position_id TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (setlist_id) REFERENCES setlists (id) ON DELETE CASCADE,
  -- We don't cascade deletes here; you won't be able to delete a song sheet
  -- if it's been attached to a set list. This is needed to preserve the
  -- record of set list songs.
  FOREIGN KEY (song_sheet_id) REFERENCES song_sheets (id),
  FOREIGN KEY (setlist_position_id) REFERENCES setlist_positions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS setlist_templates (
  id TEXT UNIQUE DEFAULT ('t:' || uuid_generate_v4()),
  title TEXT NOT NULL,
  tags TEXT[],
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS setlist_template_positions (
  id TEXT UNIQUE DEFAULT ('tp:' || uuid_generate_v4()),
  template_id TEXT NOT NULL,
  index INTEGER NOT NULL,
  label TEXT NOT NULL,
  is_music BOOLEAN,
  presenter TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (template_id) REFERENCES setlist_templates (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
  id TEXT UNIQUE DEFAULT ('c:' || uuid_generate_v4()),
  resource_id TEXT NOT NULL,
  comment TEXT NOT NULL,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);
