import requests
import json

# Coordenadas de ejemplo (ubicación actual y destino)
lat_origen, lon_origen = -33.4576196,-70.6545054  # Ejemplo: Santiago, Chile
lat_destino, lon_destino = -33.4538237,-70.6539031  # Ejemplo: otro punto en Santiago

# URL de la API de OSRM (para caminar)
url = f"http://router.project-osrm.org/route/v1/foot/{lon_origen},{lat_origen};{lon_destino},{lat_destino}?overview=full&geometries=geojson"

# Hacer la solicitud a OSRM
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear la respuesta JSON
    ruta = response.json()
    
    # Extraer la geometría de la ruta
    geojson_ruta = ruta['routes'][0]['geometry']

    # Guardar la ruta en un archivo GeoJSON
    with open('ruta.geojson', 'w') as f:
        json.dump(geojson_ruta, f)

    print("Ruta calculada y guardada en ruta.geojson")
else:
    print(f"Error al obtener la ruta: {response.status_code}")
