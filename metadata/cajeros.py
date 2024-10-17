import requests
import json

# URL de la API de cajeros automáticos
url = "https://www.redbanc.cl/redbanc/data/Cajeros.json"

# Realizar la solicitud GET
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Convertir la respuesta en JSON
    cajeros_data = response.json()
    
    # Crear un objeto GeoJSON
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Añadir cada cajero como una característica en GeoJSON
    for cajero in cajeros_data:
        # Solo agregamos los cajeros que tienen coordenadas válidas
        if cajero['LATITUD'] is not None and cajero['LONGITUD'] is not None:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [cajero['LONGITUD'], cajero['LATITUD']]
                },
                "properties": {
                    "ATM": cajero.get('ATM', 'N/A'),
                    "institucion": cajero.get('INSTITUCION', 'N/A'),
                    "direccion": cajero.get('DIRECCION', 'N/A'),
                    "comuna": cajero.get('COMUNA', 'N/A'),
                    "ciudad": cajero.get('CIUDAD', 'N/A'),
                    "region": cajero.get('REGION', 'N/A'),
                    "categoria": cajero.get('CATEGORIA', 'N/A'),
                    "estado": cajero.get('ESTADO', 'N/A')
                }
            }
            geojson_data["features"].append(feature)

    # Guardar los datos en un archivo GeoJSON
    with open('cajeros.geojson', 'w') as file:
        json.dump(geojson_data, file, indent=4)
    
    print("Datos de cajeros automáticos guardados correctamente como GeoJSON.")
else:
    print(f"Error al descargar los datos. Código de estado: {response.status_code}")