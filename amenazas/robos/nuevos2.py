import requests
import csv

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

# Definir el tamaño del paso (step) para recorrer los píxeles en el mapa.
step_size_x = 100  # Un salto de 100 píxeles en el eje X
step_size_y = 100  # Un salto de 100 píxeles en el eje Y

# Abrir el archivo CSV para escribir los resultados
with open("hexagons_data.csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Escribir el encabezado del archivo CSV (puedes modificar esto según los datos que quieras guardar)
    csv_writer.writerow(["X", "Y", "dmcs", "robos", "robos_f", "robos_v", "nivel_dmcs", "nivel_robo", "nivel_rf", "nivel_rv", "size", "id"])
    
    # Recorrer todas las coordenadas X e Y
    for x in range(0, width, step_size_x):
        for y in range(0, height, step_size_y):
            # Obtener los datos para cada píxel
            hexagon_data = get_all_hexagons(base_url, bbox, width, height, srs, x, y)
            
            if hexagon_data and "features" in hexagon_data and len(hexagon_data["features"]) > 0:
                # Si se encontraron hexágonos, procesamos los datos y los escribimos en el archivo CSV
                for feature in hexagon_data["features"]:
                    properties = feature["properties"]
                    
                    # Extraer los valores de los atributos que deseas almacenar en el CSV
                    row = [
                        x,  # Coordenada X del píxel
                        y,  # Coordenada Y del píxel
                        properties.get("dmcs", ""),
                        properties.get("robos", ""),
                        properties.get("robos_f", ""),
                        properties.get("robos_v", ""),
                        properties.get("nivel_dmcs", ""),
                        properties.get("nivel_robo", ""),
                        properties.get("nivel_rf", ""),
                        properties.get("nivel_rv", ""),
                        properties.get("size", ""),
                        properties.get("id", "")
                    ]
                    
                    # Escribir la fila en el archivo CSV
                    csv_writer.writerow(row)
                    
                print(f"Datos para el pixel {x},{y} añadidos.")
            else:
                print(f"No se obtuvieron datos para el pixel {x},{y} o no hay hexágonos.")

print("Datos guardados en hexagons_data.csv")
