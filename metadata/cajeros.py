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
    
    # Crear un diccionario para almacenar los datos de los cajeros
    cajeros_dict = {}

    # Añadir cada cajero en el diccionario
    for cajero in cajeros_data:
        # Usamos el valor del ATM como clave
        atm_id = cajero.get('ATM', 'N/A')

        # Solo añadimos los cajeros que tienen coordenadas válidas
        if cajero['LATITUD'] is not None and cajero['LONGITUD'] is not None:
            cajeros_dict[atm_id] = {
                "institucion": cajero.get('INSTITUCION', 'N/A'),
                "direccion": cajero.get('DIRECCION', 'N/A'),
                "comuna": cajero.get('COMUNA', 'N/A'),
                "ciudad": cajero.get('CIUDAD', 'N/A'),
                "region": cajero.get('REGION', 'N/A'),
                "categoria": cajero.get('CATEGORIA', 'N/A'),
                "estado": cajero.get('ESTADO', 'N/A'),
                "latitud": cajero['LATITUD'],
                "longitud": cajero['LONGITUD']
            }

    # Guardar los datos en un archivo JSON como un diccionario
    with open('cajeros.json', 'w') as file:
        json.dump(cajeros_dict, file, indent=4)
    
    print("Datos de cajeros automáticos guardados correctamente como diccionario en JSON.")
else:
    print(f"Error al descargar los datos. Código de estado: {response.status_code}")
