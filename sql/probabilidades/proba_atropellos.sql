-- Paso 1: Crear la tabla 'atropello_comuna' si no existe
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
    comuna_intersectada TEXT -- Columna para la comuna intersectada
);

-- Paso 2: Crear una tabla temporal para almacenar los atropellos intersectados
DROP TABLE IF EXISTS intersected_atropellos;
CREATE TEMP TABLE intersected_atropellos AS
WITH boundary AS (
    SELECT comuna, wkb_geometry AS geom
    FROM rm_santiago
    WHERE comuna IN ('Providencia', 'Ñuñoa')
)
SELECT 
    a.*,
    b.comuna AS comuna_intersectada
FROM 
    atropellos a
JOIN 
    boundary b
ON 
    ST_Within(a.coordenadas, b.geom); -- Intersección espacial

-- Paso 3: Crear una tabla temporal para almacenar el número de atropellos cercanos
DROP TABLE IF EXISTS atropellos_cercanos;
CREATE TEMP TABLE atropellos_cercanos AS
SELECT 
    a.id AS id_atropello,
    COUNT(b.id) AS atropellos_cercanos
FROM 
    intersected_atropellos a
JOIN 
    atropellos b
ON 
    ST_DWithin(a.coordenadas, b.coordenadas, 500) -- Radio de 500 metros
GROUP BY 
    a.id;

-- Paso 4: Calcular el total de atropellos cercanos
WITH total_cercanos AS (
    SELECT SUM(atropellos_cercanos) AS total FROM atropellos_cercanos
)
-- Paso 5: Insertar los datos en la tabla 'atropello_comuna' con la probabilidad calculada
INSERT INTO atropello_comuna (
    id_atropello, año, claseaccid, cod_regi, region, comuna, cod_zona, zona, 
    calle_uno, calle_dos, intersecci, numero, ruta, ubicacion_1, 
    siniestros, fallecidos, graves, menos_grav, leves, ilesos, coordenadas, 
    probabilidad, comuna_intersectada
)
SELECT 
    ia.id AS id_atropello, ia.año, ia.claseaccid, ia.cod_regi, ia.region, ia.comuna, 
    ia.cod_zona, ia.zona, ia.calle_uno, ia.calle_dos, ia.intersecci, ia.numero, 
    ia.ruta, ia.ubicacion_1, ia.siniestros, ia.fallecidos, ia.graves, ia.menos_grav, 
    ia.leves, ia.ilesos, ia.coordenadas,
    COALESCE(ROUND(
        (ac.atropellos_cercanos::NUMERIC / (SELECT total FROM total_cercanos)), 5
    ), 0.00001) AS probabilidad, -- Asegurar probabilidad mínima de 0.00001
    ia.comuna_intersectada
FROM 
    intersected_atropellos ia
JOIN 
    atropellos_cercanos ac
ON 
    ia.id = ac.id_atropello;
