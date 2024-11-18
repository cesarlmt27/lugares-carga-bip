-- Step 1: Create the table `cajeros_comuna` if it doesn't exist
CREATE TABLE IF NOT EXISTS cajeros_comuna (
    id SERIAL PRIMARY KEY,
    id_cajero INTEGER NOT NULL,
    atm INTEGER,
    institucion TEXT,
    categoria TEXT,
    direccion TEXT,
    comuna TEXT,
    ciudad TEXT,
    region TEXT,
    estado TEXT,
    coordenadas GEOMETRY(Point, 4326),
    comuna_intersectada TEXT,
    probabilidad FLOAT
);

-- Step 2: Define the boundary for Providencia and Ñuñoa and insert intersected cajeros
WITH boundary AS (
    SELECT comuna, wkb_geometry AS geom
    FROM rm_santiago
    WHERE comuna IN ('Providencia', 'Ñuñoa')
),
intersected_cajeros AS (
    SELECT 
        c.id AS id_cajero, c.atm, c.institucion, c.categoria, c.direccion, 
        c.comuna, c.ciudad, c.region, c.estado, c.coordenadas, 
        b.comuna AS comuna_intersectada
    FROM 
        cajeros c
    JOIN 
        boundary b
    ON 
        ST_Within(c.coordenadas, b.geom)
),
classified_cajeros AS (
    SELECT 
        id_cajero, atm, institucion, categoria, direccion, comuna, ciudad, region, estado, 
        coordenadas, comuna_intersectada,
        CASE 
            -- Assign probabilistic weights based on institution
            WHEN institucion = 'BANCO ESTADO' THEN 0.3
            WHEN institucion = 'BANCO SANTANDER' THEN 0.2
            WHEN institucion = 'BANCO SCOTIABANK' THEN 0.15
            WHEN institucion = 'BANCO BICE' THEN 0.05
            ELSE 0.1
        END +
        CASE 
            -- Assign probabilistic weights based on category
            WHEN categoria = 'CLINICA Y HOSPITALES' THEN 0.3
            WHEN categoria = 'FARMACIA' THEN 0.25
            WHEN categoria = 'Cajero VIP' THEN 0.2
            WHEN categoria = 'SUPERMERCADO' THEN 0.15
            WHEN categoria = 'ESTACION DE SERVICIO' THEN 0.1
            ELSE 0.05
        END AS probabilidad
    FROM 
        intersected_cajeros
)

-- Step 3: Insert classified data into `cajeros_comuna`
INSERT INTO cajeros_comuna (
    id_cajero, atm, institucion, categoria, direccion, comuna, ciudad, region, 
    estado, coordenadas, comuna_intersectada, probabilidad
)
SELECT 
    id_cajero, atm, institucion, categoria, direccion, comuna, ciudad, region, estado, 
    coordenadas, comuna_intersectada, probabilidad
FROM 
    classified_cajeros;
