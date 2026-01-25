CREATE VIEW song_history AS
SELECT DISTINCT
    setlists.id AS setlist_id,
    setlists.service_date AS setlist_service_date,
    song_versions.song_id
FROM song_versions
INNER JOIN song_sheets ON song_sheets.song_version_id = song_versions.id
INNER JOIN setlist_sheets ON setlist_sheets.song_sheet_id = song_sheets.id
INNER JOIN setlists ON setlists.id = setlist_sheets.setlist_id
WHERE setlist_sheets.type NOT LIKE '%candidate%'
AND setlist_sheets.setlist_position_id IS NOT NULL
AND setlists.service_date <= current_date;

-- from https://wiki.postgresql.org/wiki/First/last_(aggregate)
CREATE OR REPLACE FUNCTION public.first_agg (anyelement, anyelement)
  RETURNS anyelement
  LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS
'SELECT $1';

CREATE AGGREGATE public.first (anyelement) (
  SFUNC    = public.first_agg
, STYPE    = anyelement
, PARALLEL = safe
);

CREATE OR REPLACE FUNCTION public.last_agg (anyelement, anyelement)
  RETURNS anyelement
  LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS
'SELECT $2';

CREATE AGGREGATE public.last (anyelement) (
  SFUNC    = public.last_agg
, STYPE    = anyelement
, PARALLEL = safe
);

UPDATE _version SET ver = 6 WHERE pk = 'db_version';
