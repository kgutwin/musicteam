CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO _version (pk, ver) VALUES ('db_version', 1);

CREATE TABLE users (
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

CREATE VIEW all_authors (author, count) AS
SELECT
  DISTINCT unnest(authors) AS author,
  COUNT(*) AS count
FROM songs
GROUP BY author
ORDER BY author;

CREATE TABLE song_versions (
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

CREATE TABLE song_sheets (
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

CREATE TABLE song_media (
  id TEXT UNIQUE DEFAULT ('sm:' || uuid_generate_v4()),
  song_version_id TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT,
  object_id TEXT,
  media_type TEXT,
  tags TEXT[],
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (song_version_id) REFERENCES song_versions (id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE setlists (
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

CREATE TABLE setlist_positions (
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

CREATE TABLE setlist_sheets (
  id TEXT UNIQUE DEFAULT ('ls:' || uuid_generate_v4()),
  setlist_id TEXT NOT NULL,
  type TEXT NOT NULL,
  song_sheet_id TEXT NOT NULL,
  setlist_position_id TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (setlist_id) REFERENCES setlists (id) ON DELETE CASCADE,
  -- We don't cascade deletes here, you won't be able to delete a song sheet
  -- if it's been attached to a set list. This is needed to preserve the
  -- record of set list songs.
  FOREIGN KEY (song_sheet_id) REFERENCES song_sheets (id),
  FOREIGN KEY (setlist_position_id) REFERENCES setlist_positions (id) ON DELETE CASCADE
);

CREATE TABLE setlist_templates (
  id TEXT UNIQUE DEFAULT ('t:' || uuid_generate_v4()),
  title TEXT NOT NULL,
  tags TEXT[],
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE setlist_template_positions (
  id TEXT UNIQUE DEFAULT ('tp:' || uuid_generate_v4()),
  template_id TEXT NOT NULL,
  index INTEGER NOT NULL,
  label TEXT NOT NULL,
  is_music BOOLEAN,
  presenter TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (template_id) REFERENCES setlist_templates (id) ON DELETE CASCADE
);

CREATE TABLE comments (
  id TEXT UNIQUE DEFAULT ('c:' || uuid_generate_v4()),
  resource_id TEXT NOT NULL,
  comment TEXT NOT NULL,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE VIEW all_tags (tag, count) AS
WITH tags AS (
  SELECT unnest(tags) AS tag FROM songs
  UNION ALL
  SELECT unnest(tags) AS tag FROM song_versions
  UNION ALL
  SELECT unnest(tags) AS tag FROM song_sheets
  UNION ALL
  SELECT unnest(tags) AS tag FROM song_media
  UNION ALL
  SELECT unnest(tags) AS tag FROM setlists
  UNION ALL
  SELECT unnest(tags) AS tag FROM setlist_templates
)
SELECT tag, count(*) AS count FROM tags
GROUP BY tag
ORDER BY tag;
