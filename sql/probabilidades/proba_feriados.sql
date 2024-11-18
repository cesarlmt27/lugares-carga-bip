-- Paso 1: Crear la tabla de probabilidades si no existe 
CREATE TABLE IF NOT EXISTS feriados_probabilidad (
    id SERIAL PRIMARY KEY,
    id_feriado INT REFERENCES feriados(id),
    nombre VARCHAR(255),
    fecha DATE,
    tipo VARCHAR(50),
    irrenunciable BOOLEAN,
    probabilidad FLOAT
);

-- Paso 2: Insertar las probabilidades calculadas en la nueva tabla
INSERT INTO feriados_probabilidad (id_feriado, nombre, fecha, tipo, irrenunciable, probabilidad)
SELECT 
    id AS id_feriado,
    nombre,
    fecha,
    tipo,
    irrenunciable,
    CASE
        -- Si el feriado es irrenunciable, usar la fórmula (1927-143)/1927
        WHEN irrenunciable THEN ROUND((1927.0 - 143) / 1927, 5) 
        WHEN tipo = 'Religioso' THEN 0.5           -- Probabilidad media si es religioso
        WHEN tipo = 'Civil' THEN 0.2               -- Probabilidad baja si es civil
        ELSE 0.1                                   -- Probabilidad mínima si no se clasifica
    END AS probabilidad
FROM feriados;

-- Paso 3: Asegurar que ninguna probabilidad sea menor a 0.00001
UPDATE feriados_probabilidad
SET probabilidad = CASE
    WHEN probabilidad < 0.00001 THEN 0.00001
    ELSE probabilidad
END;

-- Verificar los resultados
SELECT * FROM feriados_probabilidad ORDER BY fecha LIMIT 10;
