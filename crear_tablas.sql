CREATE TABLE IF NOT EXISTS nodos (
    id SERIAL PRIMARY KEY,
    direccion VARCHAR(255),
    longitud DOUBLE PRECISION,
    latitud DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326)
);