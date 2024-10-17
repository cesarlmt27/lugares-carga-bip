CREATE TABLE IF NOT EXISTS nodos (
    id SERIAL PRIMARY KEY,
    direccion VARCHAR(255),
    longitud DOUBLE PRECISION,
    latitud DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326)
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

CREATE TABLE IF NOT EXISTS cajeros (
    atm INT PRIMARY KEY,
    institucion VARCHAR(255),
    direccion VARCHAR(255),
    comuna VARCHAR(100),
    ciudad VARCHAR(100),
    region VARCHAR(100),
    categoria VARCHAR(100),
    estado VARCHAR(50),
    latitud FLOAT,
    longitud FLOAT,
    coordenadas GEOMETRY(Point, 4326)
);


CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    comentarios TEXT,
    fecha DATE,
    irrenunciable BOOLEAN,
    tipo VARCHAR(50),
    leyes JSONB
);

CREATE TABLE IF NOT EXISTS robos (
    id serial PRIMARY KEY,
    feature_id varchar,
    dmcs double precision,
    robos integer,
    robos_f integer,
    robos_v integer,
    nivel_dmcs integer,
    nivel_robo integer,
    nivel_rf integer,
    nivel_rv integer,
    size double precision,
    coordenadas geography(Point, 4326)
);
