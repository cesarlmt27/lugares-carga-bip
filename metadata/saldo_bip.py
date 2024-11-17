import requests
from bs4 import BeautifulSoup
import json
import sys

def peticion_post(numero_tarjeta):
    url = f"http://pocae.tstgo.cl/PortalCAE-WAR-MODULE/SesionPortalServlet?accion=6&NumDistribuidor=99&NomUsuario=usuInternet&NomHost=AFT&NomDominio=aft.cl&Trx&RutUsuario=0&NumTarjeta={numero_tarjeta}&bloqueable="

    try:
        response = requests.post(url)
        response.raise_for_status()  # Levanta un error para códigos de estado HTTP 4xx/5xx
        
        resultado_string = response.text
        
        # Parsear el HTML de la respuesta
        soup = BeautifulSoup(resultado_string, 'html.parser')
        
        # Validar el número de tarjeta
        numero_tarjeta = int(numero_tarjeta)
        if numero_tarjeta < 0:
            print('El parámetro ingresado no cumple con los requisitos para ser aceptada como Bip!.')
            raise ValueError
        
        numero_tarjeta = str(numero_tarjeta)
        if len(numero_tarjeta) < 6 or len(numero_tarjeta) > 12:
            print('Tarjeta ingresada inválida.')
            raise ValueError
        
        # Extraer los datos deseados en un diccionario
        data_dict = {}
        keys = ['numero_tarjeta', 'estado_contrato', 'saldo_tarjeta', 'fecha_saldo']
        for i, key in enumerate(keys):
            data = soup.select('td[bgcolor="#B9D2EC"]')[i].text
            data_dict[key] = data
        
        return data_dict
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Transantiago no contesta. Respuesta HTTP: {response.status_code}.") from e
    except Exception as e:
        raise RuntimeError('Hubo un problema al obtener los datos de la tarjeta.') from e

def devuelve_tarjeta_bip(numero_tarjeta):
    try:
        data = peticion_post(numero_tarjeta)
        
        # Guardar los datos en un archivo JSON
        with open('saldo_bip.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print("Datos almacenados en 'saldo_bip.json'")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python saldo_bip.py <numero_tarjeta>")
        sys.exit(1)
    
    numero_tarjeta = sys.argv[1]
    devuelve_tarjeta_bip(numero_tarjeta)