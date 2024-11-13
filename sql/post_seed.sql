ALTER TABLE planet_osm_line
ALTER COLUMN way TYPE geometry(LineString, 4326)
USING ST_Transform(way, 4326);