CREATE TABLE setlist_recordings (
  id TEXT UNIQUE DEFAULT ('r:' || uuid_generate_v4()),
  setlist_id TEXT NOT NULL,
  tags TEXT[],
  object_id TEXT NOT NULL,
  object_type TEXT NOT NULL,
  duration DECIMAL NOT NULL,
  waveform TEXT,
  created_on TIMESTAMP DEFAULT (localtimestamp(4)),
  creator_id TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (setlist_id) REFERENCES setlists (id) ON DELETE CASCADE,
  FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE setlist_recording_marks (
  id TEXT UNIQUE DEFAULT ('rm:' || uuid_generate_v4()),
  recording_id TEXT NOT NULL,
  offset_sec DECIMAL NOT NULL,
  setlist_position_id TEXT,
  song_version_id TEXT,
  cue_title TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (recording_id) REFERENCES setlist_recordings (id) ON DELETE CASCADE,
  FOREIGN KEY (setlist_position_id) REFERENCES setlist_positions (id),
  FOREIGN KEY (song_version_id) REFERENCES song_versions (id) ON DELETE SET NULL
);

UPDATE _version SET ver = 10 WHERE pk = 'db_version';
