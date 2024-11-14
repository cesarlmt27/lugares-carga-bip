-- Transformar la columna `way` de `planet_osm_line` a SRID 4326
ALTER TABLE planet_osm_line
ALTER COLUMN way TYPE geometry(LineString, 4326)
USING ST_Transform(way, 4326);

-- Crear una única tabla `rm_line` que contiene todos los caminos que intersectan con `rm_santiago`
CREATE TABLE rm_line AS
SELECT roads.*, NULL::INTEGER AS source, NULL::INTEGER AS target, NULL::DOUBLE PRECISION AS cost
FROM planet_osm_line AS roads
JOIN rm_santiago AS boundaries
ON ST_Intersects(roads.way, boundaries.wkb_geometry)
WHERE roads.highway IS NOT NULL;

-- Calcular y actualizar `cost` usando la longitud de `way` en SRID 32719 (o el SRID adecuado)
UPDATE rm_line SET cost = ST_Length(ST_Transform(way, 32719));

-- Crear la topología para la tabla, generando `source` y `target` en cada arista
SELECT pgr_createTopology('rm_line', 0.0001, 'way', 'osm_id');