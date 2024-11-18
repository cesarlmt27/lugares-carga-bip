import geopandas as gpd
from geopy.distance import geodesic
import psycopg
from shapely.geometry import mapping
import json

# Conexión a la base de datos
conn = None
try:
    conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")
    print("Conexión exitosa a la base de datos.")
except psycopg.OperationalError as e:
    print(f"Error al conectar a la base de datos: {e}")
    exit(1)

# Cargar el archivo GeoJSON de atropellos
try:
    atropellos_gdf = gpd.read_file("/app/amenazas/atropellos.geojson")
    print(f"Se cargaron {len(atropellos_gdf)} registros de atropellos.")
except Exception as e:
    print(f"Error al cargar el archivo GeoJSON: {e}")
    exit(1)

# Obtener las coordenadas de los puntos de atropello
atropellos_puntos = []
for _, row in atropellos_gdf.iterrows():
    if row.geometry.geom_type == "MultiPoint":
        for point in row.geometry.geoms:
            atropellos_puntos.append((point.x, point.y))
    elif row.geometry.geom_type == "Point":
        atropellos_puntos.append((row.geometry.x, row.geometry.y))
    else:
        print(f"Geometría no soportada: {row.geometry.geom_type}")

# Función para calcular cuántos puntos están dentro de un radio de 1000 metros
def obtener_atropellos_cercanos(geometry, puntos_atropellos, radio=1000):
    cercanos = 0
    if geometry.geom_type == "Point":
        punto = (geometry.y, geometry.x)
        for otro_punto in puntos_atropellos:
            distancia = geodesic(punto, (otro_punto[1], otro_punto[0])).meters
            if distancia <= radio:
                cercanos += 1
    elif geometry.geom_type == "MultiPoint":
        for point in geometry.geoms:
            punto = (point.y, point.x)
            for otro_punto in puntos_atropellos:
                distancia = geodesic(punto, (otro_punto[1], otro_punto[0])).meters
                if distancia <= radio:
                    cercanos += 1
    else:
        print(f"Tipo de geometría no soportado: {geometry.geom_type}")
    return cercanos

# Calcular atropellos cercanos y la probabilidad
atropellos_gdf['atropellos_cercanos'] = atropellos_gdf['geometry'].apply(
    lambda geom: obtener_atropellos_cercanos(geom, atropellos_puntos)
)

total_atropellos = atropellos_gdf['atropellos_cercanos'].sum()
if total_atropellos > 0:
    atropellos_gdf['probabilidad_falla'] = atropellos_gdf['atropellos_cercanos'] / total_atropellos
else:
    atropellos_gdf['probabilidad_falla'] = 0

# Actualizar la base de datos con las probabilidades calculadas
update_query = """
UPDATE atropellos
SET probabilidad_falla = %s
WHERE ST_Equals(coordenadas, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
"""

with conn.cursor() as cur:
    for _, row in atropellos_gdf.iterrows():
        geom_json = json.dumps(mapping(row['geometry']))  # Convertir la geometría a formato GeoJSON
        cur.execute(update_query, (
            row['probabilidad_falla'],  # Probabilidad calculada
            geom_json                  # Geometría en formato GeoJSON
        ))

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Probabilidades de atropellos actualizadas en la tabla 'atropellos'.")
