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

# Inicializar el archivo JSON
with open("robos.json", 'w') as json_file:
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
    }, json_file)

# Definir el tamaño del paso (step) para recorrer los píxeles en el mapa.
step_size_x = 25
step_size_y = 25

# Abrir el archivo en modo lectura y escritura (r+), para agregar cada nuevo hexágono
with open("robos.json", 'r+') as json_file:
    data = json.load(json_file)
    hexagon_count = 0
    
    for x in range(0, width, step_size_x):
        for y in range(0, height, step_size_y):
            hexagon_data = get_all_hexagons(base_url, bbox, width, height, srs, x, y)
            
            if hexagon_data and "features" in hexagon_data and len(hexagon_data["features"]) > 0:
                data["features"].extend(hexagon_data["features"])
                hexagon_count += len(hexagon_data["features"])
                print(f"Datos para el pixel {x},{y} añadidos.")
            else:
                print(f"No se obtuvieron datos para el pixel {x},{y} o no hay hexágonos.")

    data["numberReturned"] = hexagon_count
    data["timeStamp"] = datetime.now().isoformat()

    json_file.seek(0)
    json.dump(data, json_file, indent=4)
    print("Datos guardados en robos.json")


# Get para postman:
# https://stop.carabineros.cl/geoserver/stop/wms/?service=WMS&request=GetMap&version=1.1.1&layers=stop%3ARobosFuerza&styles=&format=image%2Fpng&transparent=true&info_format=application%2Fjson&width=5088&height=2954&srs=EPSG%3A3857&bbox=-7889476.538413658%2C-3970263.864888263%2C-7840862.588424286%2C-3942039.4921939606