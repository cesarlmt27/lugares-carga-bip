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

-- Crear la tabla 'cajero_comuna'
CREATE TABLE IF NOT EXISTS cajero_comuna (
    id SERIAL PRIMARY KEY,
    id_cajero INTEGER NOT NULL,
    atm INTEGER NOT NULL,
    institucion TEXT,
    direccion TEXT,
    comuna TEXT,
    ciudad TEXT,
    region TEXT,
    categoria TEXT,
    estado TEXT,
    coordenadas GEOMETRY(Point, 4326),
    probabilidad FLOAT,
    comuna_intersectada TEXT -- Columna para la comuna intersecada
);

-- Insertar datos con intersección entre 'cajeros' y 'rm_santiago'
WITH boundary AS (
    SELECT comuna, wkb_geometry AS geom
    FROM rm_santiago
    WHERE comuna IN ('Providencia', 'Ñuñoa')
)
INSERT INTO cajero_comuna (
    id_cajero, atm, institucion, direccion, comuna, ciudad, region, categoria, 
    estado, coordenadas, comuna_intersectada
)
SELECT 
    c.id AS id_cajero, c.atm, c.institucion, c.direccion, c.comuna, 
    c.ciudad, c.region, c.categoria, c.estado, c.coordenadas, b.comuna AS comuna_intersectada
FROM cajeros c
JOIN boundary b
ON ST_Within(c.coordenadas, b.geom);

-- Crear la tabla 'atropello_comuna'
CREATE TABLE IF NOT EXISTS atropello_comuna (
    id SERIAL PRIMARY KEY,
    id_atropello INTEGER NOT NULL,
    año INTEGER NOT NULL,
    claseaccid INTEGER,
    cod_regi INTEGER,
    region TEXT,
    comuna TEXT,
    cod_zona INTEGER,
    zona TEXT,
    calle_uno TEXT,
    calle_dos TEXT,
    intersecci TEXT,
    numero INTEGER,
    ruta TEXT,
    ubicacion_1 TEXT,
    siniestros INTEGER,
    fallecidos INTEGER,
    graves INTEGER,
    menos_grav INTEGER,
    leves INTEGER,
    ilesos INTEGER,
    coordenadas GEOMETRY(Point, 4326),
    probabilidad FLOAT,
    comuna_intersectada TEXT -- Columna para la comuna intersecada
);

-- Insertar datos con intersección entre 'atropellos' y 'rm_santiago'
WITH boundary AS (
    SELECT comuna, wkb_geometry AS geom
    FROM rm_santiago
    WHERE comuna IN ('Providencia', 'Ñuñoa')
)
INSERT INTO atropello_comuna (
    id_atropello, año, claseaccid, cod_regi, region, comuna, cod_zona, zona, 
    calle_uno, calle_dos, intersecci, numero, ruta, ubicacion_1, 
    siniestros, fallecidos, graves, menos_grav, leves, ilesos, coordenadas, comuna_intersectada
)
SELECT 
    a.id AS id_atropello, a.año, a.claseaccid, a.cod_regi, a.region, a.comuna, 
    a.cod_zona, a.zona, a.calle_uno, a.calle_dos, a.intersecci, a.numero, a.ruta, 
    a.ubicacion_1, a.siniestros, a.fallecidos, a.graves, a.menos_grav, 
    a.leves, a.ilesos, a.coordenadas, b.comuna AS comuna_intersectada
FROM atropellos a
JOIN boundary b
ON ST_Within(a.coordenadas, b.geom);

