import requests
import json

def get_hexagon_data(api_url, output_file):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Verifica si hubo errores HTTP
        # Acepta cualquier respuesta que contenga 'application/json'
        if 'application/json' in response.headers.get('content-type'):
            data = response.json()  # Intenta decodificar la respuesta como JSON
            with open(output_file, 'w') as f:
                json.dump(data, f)
            print(f"Datos guardados en {output_file}")
        else:
            print(f"Error: La respuesta no es JSON. Content-Type: {response.headers.get('content-type')}")
    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error en la solicitud: {err}")
    except json.JSONDecodeError as errj:
        print(f"Error al decodificar JSON: {errj}")
        print("Contenido de la respuesta:", response.text)

# URL de ejemplo para la API
api_url = "https://stop.carabineros.cl/geoserver/stop/wms/?service=WMS&request=GetFeatureInfo&version=1.1.1&layers=stop%3ARobos&query_layers=stop%3ARobos&styles=&format=image%2Fpng&transparent=true&info_format=application%2Fjson&width=1528&height=666&srs=EPSG%3A3857&bbox=-7893384.381411156%2C-3970292.949955734%2C-7834986.4918012805%2C-3944839.4195367713&X=768&Y=345"

# Nombre del archivo de salida
output_file = "hexagons_data.json"

# Llamar a la función
get_hexagon_data(api_url, output_file)
