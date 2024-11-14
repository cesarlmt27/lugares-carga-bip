import json
import pandas as pd
import warnings
from pyproj import Transformer

# Ignorar advertencias de duplicados en los IDs
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*found.*")

# Rutas de los archivos
robos_path = "../amenazas/robos.json"
output_probabilidades_path = "../probabilidades/probabilidad_fallas.csv"

# Crear el transformador de EPSG:3857 a EPSG:4326
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

# Función para transformar coordenadas
def transformar_coordenadas(x, y):
    return transformer.transform(x, y)

# Cargar los datos de robos
with open(robos_path, 'r', encoding='utf-8') as f:
    robos_data = json.load(f)

# Crear un DataFrame para almacenar los resultados
robos_df = pd.json_normalize(robos_data["features"])

# Transformar la id numérica para que tenga el mismo valor que la id del feature
robos_df["id"] = robos_df.apply(lambda row: row["id"].split(".")[0] + "." + str(row["properties.id"]) if isinstance(row["id"], str) else str(row["properties.id"]), axis=1)

# Función para obtener todas las coordenadas de los vértices y transformarlas
def obtener_y_transformar_coordenadas(row):
    coordenadas_transformadas = []
    try:
        # Recorrer cada polígono dentro del MultiPolygon
        for polygon in row["geometry.coordinates"]:
            for coords in polygon:
                for coord in coords:
                    # Transformar cada vértice
                    x, y = coord
                    transformed_x, transformed_y = transformar_coordenadas(x, y)
                    coordenadas_transformadas.append((transformed_x, transformed_y))
    except (IndexError, TypeError) as e:
        # En caso de error, devolver lista vacía
        return []
    return coordenadas_transformadas

# Aplicar la función a cada fila para obtener todas las coordenadas transformadas
robos_df["coordenadas_transformadas"] = robos_df.apply(obtener_y_transformar_coordenadas, axis=1)

# Calcular el total de robos registrados
total_robos_registrados = robos_df["properties.robos"].astype(int).sum()

# Calcular la probabilidad de falla como la cantidad de robos totales en la zona dividido por los robos totales registrados
robos_df["probabilidad_falla"] = robos_df["properties.robos"].astype(int) / total_robos_registrados

# Crear un DataFrame de resultados donde se almacenarán las coordenadas de cada vértice junto con el id y la probabilidad de falla
resultados_df = pd.DataFrame(columns=["id", "longitude", "latitude", "probabilidad_falla"])

# Recorrer las filas del DataFrame y agregar cada vértice a 'resultados_df'
for _, row in robos_df.iterrows():
    id_hexagono = row["id"]
    probabilidad_falla = row["probabilidad_falla"]
    coordenadas = row["coordenadas_transformadas"]
    
    # Crear un DataFrame temporal para los vértices de cada hexágono
    temp_df = pd.DataFrame(coordenadas, columns=["longitude", "latitude"])
    temp_df["id"] = id_hexagono
    temp_df["probabilidad_falla"] = probabilidad_falla
    
    # Concatenar con el DataFrame de resultados
    resultados_df = pd.concat([resultados_df, temp_df], ignore_index=True)

# Guardar los resultados en archivo CSV
resultados_df.to_csv(output_probabilidades_path, index=False)
print(f"Archivo de probabilidades de fallas guardado en '{output_probabilidades_path}'.")
