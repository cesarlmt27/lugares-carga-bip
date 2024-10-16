import os
import requests
import pandas as pd

def descargar_y_procesar_xlsx(url, nombre_archivo):
    # Crear el directorio 'archivos' si no existe
    if not os.path.exists('archivos'):
        os.makedirs('archivos')

    # Realizar la solicitud GET para descargar el archivo
    response = requests.get(url)

    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        # Guardar el contenido en un archivo local dentro del directorio 'archivos'
        archivo_local = os.path.join('archivos', f'{nombre_archivo}.xlsx')
        with open(archivo_local, 'wb') as file:
            file.write(response.content)
        
        # Leer el archivo .xlsx
        df = pd.read_excel(archivo_local, header=None)
        
        # Buscar la fila que contiene 'CODIGO' en la primera columna
        header_row_index = df[df.iloc[:, 0] == 'CODIGO'].index[0]
        
        # Establecer esa fila como el header del DataFrame
        df.columns = df.iloc[header_row_index]
        df = df[header_row_index + 1:]
        
        # Eliminar las columnas no deseadas
        columnas_a_eliminar = ['ESTE', 'NORTE', 'LONGITUD', 'LATITUD']
        df = df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns])
        
        # Imprimir el nombre del DataFrame
        print(f"DataFrame del archivo: {nombre_archivo}.xlsx")
        
        # Imprimir el DataFrame desde el header hacia abajo
        print(df)
        print("\n")
    else:
        print(f"Error al descargar el archivo: {response.status_code}")

# Diccionario de datos
datos = {
    'retail': 'https://datos.gob.cl/dataset/f0fad229-d59a-4992-8c7a-489d1e9ff58c/resource/2d177f41-08f9-471a-af5c-bc949267f053/download',
    'estandar_normal': 'https://datos.gob.cl/dataset/29a758f3-4fe8-4582-afc7-8237b83aaddc/resource/8e827306-e9ef-4e84-a251-38d29a8f66d0/download',
    'alto_estandar': 'https://datos.gob.cl/dataset/5993b4cb-869c-4733-a124-7fcdd57bbb05/resource/fef2a0f6-84f8-4a1a-9a64-e2424efdd376/download',
    'puntos_bip': 'https://datos.gob.cl/dataset/c2969d8a-df82-4a6c-a1f8-e5eba36af6cf/resource/cbd329c6-9fe6-4dc1-91e3-a99689fd0254/download',
    'estaciones_metro': 'https://datos.gob.cl/dataset/ac76c913-3ad2-4831-ab2a-3b0d4165abdd/resource/3d54e961-d81b-4507-aeee-7a433e00a9bf/download'
}

# Iterar sobre el diccionario y llamar a la función para cada URL
for nombre_archivo, url in datos.items():
    descargar_y_procesar_xlsx(url, nombre_archivo)