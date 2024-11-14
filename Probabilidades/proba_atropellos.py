import pandas as pd
import geopandas as gpd
from geopy.distance import geodesic

# Cargar el archivo de nodos
nodos_df = pd.read_csv("../infraestructura/nodos/nodos.csv")

# Cargar el archivo GeoJSON de atropellos
atropellos_gdf = gpd.read_file("../amenazas/atropellos.geojson")

# Obtener las coordenadas de los puntos de atropello (suponiendo que son de tipo MultiPoint)
atropellos_puntos = []
for _, row in atropellos_gdf.iterrows():
    # Si la geometría es MultiPoint, iterar sobre sus puntos
    if row['geometry'].geom_type == 'MultiPoint':
        for coord in row['geometry'].geoms:  # `.geoms` devuelve un iterable de puntos
            atropellos_puntos.append((coord.x, coord.y))  # Agregar las coordenadas (x, y)
    else:
        # Si es un Point individual, agregarlo directamente
        atropellos_puntos.append((row['geometry'].x, row['geometry'].y))

# Función para calcular cuántos puntos de atropello están dentro de un radio de 1000 metros
def obtener_atropellos_cercanos(nodo, puntos_atropellos, radio=1000):
    cercanos = 0
    for punto in puntos_atropellos:
        distancia = geodesic((nodo['latitud'], nodo['longitud']), (punto[1], punto[0])).meters
        if distancia <= radio:
            cercanos += 1
    return cercanos

# Contar atropellos cercanos para cada nodo y calcular la probabilidad
total_atropellos = 1420
nodos_df['atropellos_cercanos'] = nodos_df.apply(lambda nodo: obtener_atropellos_cercanos(nodo, atropellos_puntos), axis=1)
nodos_df['probabilidad_atropellos'] = nodos_df['atropellos_cercanos'] / total_atropellos

# Guardar los resultados en un archivo CSV
nodos_df.to_csv('nodos_con_probabilidad_atropellos.csv', index=False)

print("Archivo de nodos con la cantidad y probabilidad de atropellos cercanos guardado.")