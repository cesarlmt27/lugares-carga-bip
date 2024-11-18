import requests   
import json
from datetime import datetime
import urllib3

# Desactivar las advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_hexagons(base_url, bbox, width, height, srs, x, y, timeout=30):
    params = {
        'service': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': 'stop:RobosFuerza',
        'query_layers': 'stop:RobosFuerza',
        'styles': '',
        'format': 'image/png',
        'transparent': 'true',
        'info_format': 'application/json',
        'width': width,
        'height': height,
        'srs': srs,
        'bbox': bbox,
        'X': x,
        'Y': y
    }

    try:
        response = requests.get(base_url, params=params, verify=False, timeout=timeout)
        
        # Verificar el código de estado
        if response.status_code != 200:
            print(f"Error {response.status_code}: No se pudieron obtener los datos.")
            return None

        # Verificar el tipo de contenido
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            print(f"Error: La respuesta no es JSON. Content-Type: {content_type}")
            return None

        # Intentar decodificar la respuesta como JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Error al decodificar JSON. Respuesta del servidor:")
            print(response.text[:500])  # Mostrar los primeros 500 caracteres de la respuesta
            return None

    except requests.exceptions.ReadTimeout:
        print(f"Error: La solicitud para el pixel {x},{y} excedió el tiempo de espera.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Error de conexión: {e}")
        return None

# Parámetros para la solicitud
base_url = "https://stop.carabineros.cl/geoserver/stop/wms/"
bbox = "-7889476.538413658,-3970263.864888263,-7840862.588424286,-3942039.4921939606"
width = 5088
height = 2954
srs = "EPSG:3857"

# Inicializar el archivo GeoJSON
output_file = "robos.geojson"

with open(output_file, 'w') as geojson_file:
    json.dump({
        "type": "FeatureCollection",
        "features": [],
        "totalFeatures": "unknown",
        "numberReturned": 0,
        "timeStamp": datetime.now().isoformat(),
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::3857"
            }
        }
    }, geojson_file)

# Definir el tamaño del paso (step) para recorrer los píxeles en el mapa.
step_size_x = 50
step_size_y = 25

# Función para verificar si un *feature* ya existe en la lista
def feature_duplicado(nuevo_feature, lista_features):
    for feature in lista_features:
        if (nuevo_feature["geometry"] == feature["geometry"] and
            nuevo_feature["properties"] == feature["properties"]):
            return True
    return False

# Abrir el archivo en modo lectura y escritura (r+), para agregar cada nuevo hexágono
with open(output_file, 'r+') as geojson_file:
    data = json.load(geojson_file)
    hexagon_count = 0
    
    for x in range(0, width, step_size_x):
        for y in range(0, height, step_size_y):
            # Detener el proceso si ya se alcanzaron 10 hexágonos únicos
            if hexagon_count >= 10:
                print("Se alcanzó el límite de 10 hexágonos. Finalizando el proceso.")
                break

            hexagon_data = get_all_hexagons(base_url, bbox, width, height, srs, x, y)
            
            if hexagon_data and "features" in hexagon_data and len(hexagon_data["features"]) > 0:
                for feature in hexagon_data["features"]:
                    # Verificar si el *feature* ya existe antes de agregarlo
                    if not feature_duplicado(feature, data["features"]):
                        data["features"].append(feature)
                        hexagon_count += 1
                        print(f"Feature añadido para el pixel {x},{y}. Hexágonos encontrados: {hexagon_count}")
                    else:
                        print(f"Feature duplicado omitido para el pixel {x},{y}.")
            else:
                print(f"No se obtuvieron datos para el pixel {x},{y} o no hay hexágonos.")
        if hexagon_count >= 10:
            break

    #data["numberReturned"] = hexagon_count
    #data["timeStamp"] = datetime.now().isoformat()

    geojson_file.seek(0)
    json.dump(data, geojson_file, indent=4)
    geojson_file.truncate()
    print(f"Datos guardados en {output_file}")
