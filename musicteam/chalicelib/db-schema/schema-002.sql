CREATE FUNCTION jsonb_to_text_array(_json JSONB) RETURNS TEXT [] AS $$
    SELECT array(SELECT jsonb_array_elements_text(_json))
$$ LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE;

UPDATE _version SET ver = 2 WHERE pk = 'db_version';
