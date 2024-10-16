CREATE TABLE IF NOT EXISTS nodos (
    uuid UUID NOT NULL,
    longitud DOUBLE PRECISION,
    latitud DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326),
    PRIMARY KEY (uuid)
);

CREATE TABLE caminos (
    osm_id BIGINT PRIMARY KEY,         -- ID único del camino
    highway VARCHAR(255),              -- Tipo de camino (calle, avenida, etc.)
    name VARCHAR(255),                 -- Nombre del camino
    geom GEOMETRY(LineString, 4326)    -- Geometría en formato LineString con SRID 4326 (WGS 84)
);

-- Crear un índice espacial para acelerar las consultas espaciales
CREATE INDEX idx_caminos_geom ON caminos USING GIST (geom);


CREATE TABLE IF NOT EXISTS informacion (
    uuid UUID NOT NULL,
    codigo VARCHAR(255),
    entidad VARCHAR(255),
    direccion VARCHAR(255),
    comuna VARCHAR(255),
    horario VARCHAR(255),
    PRIMARY KEY (uuid),
    FOREIGN KEY (uuid) REFERENCES nodos(uuid)
);

CREATE TABLE IF NOT EXISTS cajeros (
    id SERIAL PRIMARY KEY,
    atm INTEGER,
    institucion VARCHAR(255),
    direccion VARCHAR(255),
    comuna VARCHAR(255),
    ciudad VARCHAR(255),
    region VARCHAR(255),
    categoria VARCHAR(255),
    estado VARCHAR(50),
    coordenadas GEOMETRY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS saldo (
    numero_tarjeta VARCHAR(50) PRIMARY KEY,
    estado_contrato VARCHAR(50),
    saldo_tarjeta VARCHAR(20),
    fecha_saldo TIMESTAMP
);


CREATE TABLE IF NOT EXISTS atropellos (
    id SERIAL PRIMARY KEY,
    año INT,
    claseaccid INT,
    cod_regi INT,
    region VARCHAR(255),
    comuna VARCHAR(255),
    cod_zona INT,
    zona VARCHAR(50),
    calle_uno VARCHAR(255),
    calle_dos VARCHAR(255),
    intersecci VARCHAR(255),
    numero INT,
    ruta VARCHAR(255),
    ubicacion_1 VARCHAR(50),
    siniestros INT,
    fallecidos INT,
    graves INT,
    menos_grav INT,
    leves INT,
    ilesos INT,
    coordenadas GEOMETRY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    comentarios VARCHAR(255),
    fecha DATE,
    irrenunciable BOOLEAN,
    tipo VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS robos (
    id SERIAL PRIMARY KEY,
    dmcs INTEGER,
    robos INTEGER,
    robos_f INTEGER,
    robos_v INTEGER,
    nivel_dmcs INTEGER,
    nivel_robo INTEGER,
    nivel_rf INTEGER,
    nivel_rv INTEGER,
    size INTEGER,
    geom geometry(MultiPolygon, 4326) -- Tipo geometry para multipolígonos
);