-- Crear extensiones
CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;

-- Crear tabla nodos
CREATE TABLE IF NOT EXISTS nodos (
    id SERIAL PRIMARY KEY,             -- ID único del nodo
    longitud DOUBLE PRECISION,         -- Longitud geográfica del nodo
    latitud DOUBLE PRECISION,          -- Latitud geográfica del nodo
    geom GEOMETRY(Point, 4326)         -- Geometría del nodo en formato Point con SRID 4326 (WGS 84)
);

-- Crear tabla información
CREATE TABLE IF NOT EXISTS informacion (
    id SERIAL PRIMARY KEY,             -- ID único de la información, referencia a la tabla nodos
    codigo VARCHAR(255),               -- Código de la entidad
    entidad VARCHAR(255),              -- Nombre de la entidad
    direccion VARCHAR(255),            -- Dirección de la entidad
    comuna VARCHAR(255),               -- Comuna de la entidad
    horario VARCHAR(255),              -- Horario de atención de la entidad
    FOREIGN KEY (id) REFERENCES nodos(id) -- Clave foránea que referencia a la tabla nodos
);

-- Crear tabla cajeros
CREATE TABLE IF NOT EXISTS cajeros (
    id SERIAL PRIMARY KEY,             -- ID único del cajero
    atm INTEGER,                       -- Número del cajero automático
    institucion VARCHAR(255),          -- Institución a la que pertenece el cajero
    direccion VARCHAR(255),            -- Dirección del cajero
    comuna VARCHAR(255),               -- Comuna donde se encuentra el cajero
    ciudad VARCHAR(255),               -- Ciudad donde se encuentra el cajero
    region VARCHAR(255),               -- Región donde se encuentra el cajero
    categoria VARCHAR(255),            -- Categoría del cajero
    estado VARCHAR(50),                -- Estado del cajero
    coordenadas GEOMETRY(Point, 4326)  -- Coordenadas geográficas del cajero en formato Point con SRID 4326 (WGS 84)
);

-- Crear tabla saldo
CREATE TABLE IF NOT EXISTS saldo (
    numero_tarjeta VARCHAR(50) PRIMARY KEY, -- Número de la tarjeta, clave primaria
    estado_contrato VARCHAR(50),            -- Estado del contrato de la tarjeta
    saldo_tarjeta VARCHAR(20),              -- Saldo disponible en la tarjeta
    fecha_saldo TIMESTAMP                   -- Fecha y hora del saldo
);

-- Crear tabla atropellos
CREATE TABLE IF NOT EXISTS atropellos (
    id SERIAL PRIMARY KEY,             -- ID único del registro de atropello
    año INT,                           -- Año del atropello
    claseaccid INT,                    -- Clase de accidente
    cod_regi INT,                      -- Código de la región
    region VARCHAR(255),               -- Nombre de la región
    comuna VARCHAR(255),               -- Nombre de la comuna
    cod_zona INT,                      -- Código de la zona
    zona VARCHAR(50),                  -- Nombre de la zona
    calle_uno VARCHAR(255),            -- Primera calle involucrada
    calle_dos VARCHAR(255),            -- Segunda calle involucrada
    intersecci VARCHAR(255),           -- Intersección
    numero INT,                        -- Número de la dirección
    ruta VARCHAR(255),                 -- Ruta
    ubicacion_1 VARCHAR(50),           -- Ubicación específica
    siniestros INT,                    -- Número de siniestros
    fallecidos INT,                    -- Número de fallecidos
    graves INT,                        -- Número de heridos graves
    menos_grav INT,                    -- Número de heridos menos graves
    leves INT,                         -- Número de heridos leves
    ilesos INT,                        -- Número de ilesos
    coordenadas GEOMETRY(Point, 4326),  -- Coordenadas geográficas del atropello en formato Point con SRID 4326 (WGS 84)
    probabilidad_falla FLOAT
);

-- Crear tabla feriados
CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL PRIMARY KEY,             -- ID único del feriado
    nombre VARCHAR(255),               -- Nombre del feriado
    comentarios VARCHAR(255),          -- Comentarios sobre el feriado
    fecha DATE,                        -- Fecha del feriado
    irrenunciable BOOLEAN,             -- Indica si el feriado es irrenunciable
    tipo VARCHAR(50)                   -- Tipo de feriado
);

-- Crear tabla robos
CREATE TABLE IF NOT EXISTS robos (
    id SERIAL PRIMARY KEY,             -- ID único del registro de robo
    dmcs INTEGER,                      -- DMCs
    robos INTEGER,                     -- Número de robos
    robos_f INTEGER,                   -- Número de robos frustrados
    robos_v INTEGER,                   -- Número de robos violentos
    nivel_dmcs INTEGER,                -- Nivel de DMCs
    nivel_robo INTEGER,                -- Nivel de robos
    nivel_rf INTEGER,                  -- Nivel de robos frustrados
    nivel_rv INTEGER,                  -- Nivel de robos violentos
    size INTEGER,                      -- Tamaño
    geom GEOMETRY(MultiPolygon, 4326),  -- Geometría en formato MultiPolygon con SRID 4326 (WGS 84)
    probabilidad_falla FLOAT
);