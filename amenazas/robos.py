import requests
import json
from datetime import datetime

def get_all_hexagons(base_url, bbox, width, height, srs, x, y):
    # Construye la URL con los parámetros necesarios
    params = {
        'service': 'WMS',
        'request': 'GetFeatureInfo',
        'version': '1.1.1',
        'layers': 'stop:Robos',
        'query_layers': 'stop:Robos',
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
    
    # Realiza la solicitud GET
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        # Si la respuesta es exitosa, devuelve los datos en JSON
        return response.json()
    else:
        print(f"Error {response.status_code}: No se pudieron obtener los datos.")
        return None

# Parámetros para la solicitud
base_url = "https://stop.carabineros.cl/geoserver/stop/wms/"
bbox = "-7888224.882001906,-3968839.819651207,-7836324.139796271,-3947093.485104075"
width = 1358
height = 569
srs = "EPSG:3857"

# Creamos un archivo JSON y escribimos la estructura inicial
with open("all_hexagons_data.json", 'w') as json_file:
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
step_size_x = 50  # Un salto de 50 píxeles en el eje X
step_size_y = 50  # Un salto de 50 píxeles en el eje Y

# Abrir el archivo en modo lectura y escritura (r+), para agregar cada nuevo hexágono
with open("all_hexagons_data.json", 'r+') as json_file:
    data = json.load(json_file)  # Leer los datos existentes
    
    # Recorrer todas las coordenadas X e Y
    hexagon_count = 0  # Contador de hexágonos encontrados
    for x in range(0, width, step_size_x):
        for y in range(0, height, step_size_y):
            # Obtener los datos para cada píxel
            hexagon_data = get_all_hexagons(base_url, bbox, width, height, srs, x, y)
            
            if hexagon_data and "features" in hexagon_data and len(hexagon_data["features"]) > 0:
                # Si se encontraron hexágonos, agregarlos a la estructura existente
                data["features"].extend(hexagon_data["features"])
                hexagon_count += len(hexagon_data["features"])  # Incrementar el contador de hexágonos
                print(f"Datos para el pixel {x},{y} añadidos.")
            else:
                print(f"No se obtuvieron datos para el pixel {x},{y} o no hay hexágonos.")
    
    # Actualizar los campos adicionales
    data["numberReturned"] = hexagon_count
    data["timeStamp"] = datetime.now().isoformat()

    # Guardar los datos actualizados en el archivo JSON
    json_file.seek(0)
    json.dump(data, json_file, indent=4)
    print("Datos guardados en all_hexagons_data.json")
