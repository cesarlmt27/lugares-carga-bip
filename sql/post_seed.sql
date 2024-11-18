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

-- 1. Crear la tabla rm_comuna con datos ampliados y cálculo directo de costos
CREATE TABLE rm_comuna AS
SELECT 
    roads.*, 
    NULL::INTEGER AS source, 
    NULL::INTEGER AS target, 
    ST_Length(ST_Transform(roads.way, 32719)) AS cost -- Calcular costos directamente
FROM planet_osm_line AS roads
JOIN (
    SELECT ST_Union(wkb_geometry) AS geom
    FROM rm_santiago
    WHERE comuna IN ('Ñuñoa', 'Providencia')
) AS boundary
ON ST_Intersects(roads.way, boundary.geom)
WHERE 
    highway IN ('footway', 'path', 'pedestrian', 'living_street', 'steps', 'platform', 
                'residential', 'service', 'unclassified', 'track', 'cycleway', 
                'tertiary', 'secondary', 'tertiary_link', 'secondary_link', 
                'primary', 'primary_link', 'construction') 
    AND way IS NOT NULL;

-- 2. Generar la topología con mayor tolerancia para conectar nodos cercanos
SELECT pgr_createTopology('rm_comuna', 0.0001, 'way', 'osm_id');


