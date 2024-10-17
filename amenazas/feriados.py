import requests
import json
from time import sleep

# URL de la API de feriados nacionales
url = "https://apis.digital.gob.cl/fl/feriados"

# Encabezados para la solicitud
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Intentar hacer la solicitud con un timeout y múltiples intentos
max_retries = 3
timeout = 10  # Tiempo de espera en segundos

for attempt in range(max_retries):
    try:
        # Realizar la solicitud GET con un timeout y encabezados
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Convertir la respuesta en JSON
            feriados_data = response.json()
            
            # Guardar los datos en un archivo JSON
            with open('feriados_nacionales.json', 'w', encoding='utf-8') as file:
                json.dump(feriados_data, file, indent=4, ensure_ascii=False)
            
            print("Datos de feriados nacionales guardados correctamente en feriados_nacionales.json.")
            break  # Salir del bucle si la solicitud fue exitosa
        else:
            print(f"Error al descargar los datos. Código de estado: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"Intento {attempt + 1}: La solicitud ha excedido el tiempo de espera.")
    except requests.exceptions.ConnectionError as e:
        print(f"Intento {attempt + 1}: Error de conexión: {e}")
    
    # Esperar antes de volver a intentar
    sleep(5)
else:
    print("Error: No se pudo descargar los datos después de varios intentos.")