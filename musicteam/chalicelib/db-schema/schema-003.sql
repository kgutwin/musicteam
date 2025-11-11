ALTER TABLE song_sheets ADD COLUMN auto_verse_order BOOLEAN;
UPDATE song_sheets SET auto_verse_order = TRUE;

ALTER TABLE setlists ADD COLUMN title TEXT;
ALTER TABLE setlists ADD COLUMN participants TEXT[];

UPDATE _version SET ver = 3 WHERE pk = 'db_version';
