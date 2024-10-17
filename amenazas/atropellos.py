import requests

# URL de la API REST con el formato GeoJSON
url = "https://services3.arcgis.com/vaJl1B5HEzZj7154/arcgis/rest/services/Atropellos_RM_2022/FeatureServer/0/query"

# Parámetros de la consulta
params = {
    'where': '1=1',  # Obtener todos los datos
    'outFields': '*',  # Obtener todos los campos
    'outSR': '4326',  # Sistema de referencia espacial (WGS 84)
    'f': 'geojson'  # Formato de salida: GeoJSON
}

# Realizar la solicitud GET a la API
response = requests.get(url, params=params)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Guardar el contenido de la respuesta en un archivo GeoJSON
    with open('atropellos.geojson', 'w') as file:
        file.write(response.text)
    print("Archivo GeoJSON descargado correctamente.")
else:
    print(f"Error al descargar los datos. Código de estado: {response.status_code}")