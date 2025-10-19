CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE _version;
CREATE TABLE _version (pk TEXT PRIMARY KEY, major INT, minor INT, patch INT);
INSERT INTO _version (pk, major, minor, patch)
VALUES ('db_version', 0, 1, 0);

DROP TABLE songs;
DROP TABLE users;

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
  credits TEXT,
  ccli_num INTEGER,
  tags TEXT,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (creator_id) REFERENCES users (id)
);
