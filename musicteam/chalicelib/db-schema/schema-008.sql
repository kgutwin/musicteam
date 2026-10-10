CREATE UNIQUE INDEX ON setlist_sheets (song_sheet_id, setlist_position_id)
WHERE setlist_position_id IS NOT NULL;

UPDATE _version SET ver = 8 WHERE pk = 'db_version';
