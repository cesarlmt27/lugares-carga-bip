import os
import pandas as pd
from geoalchemy2 import WKTElement

def procesar_archivos(directorio):
    # Crear el directorio 'modificados' si no existe
    if not os.path.exists('modificados'):
        os.makedirs('modificados')
    
    # Iterar sobre los archivos en el directorio
    for archivo in os.listdir(directorio):
        if archivo.endswith('.xlsx'):
            # Leer el archivo .xlsx
            archivo_path = os.path.join(directorio, archivo)
            df = pd.read_excel(archivo_path, header=None)
            
            # Buscar la fila que contiene 'CODIGO' en la primera columna
            header_row_index = df[df.iloc[:, 0] == 'CODIGO'].index[0]
            
            # Establecer esa fila como el header del DataFrame
            df.columns = df.iloc[header_row_index]
            df = df[header_row_index + 1:]
            
            # Convertir los nombres de las columnas a minúsculas
            df.columns = df.columns.str.lower()
            
            # Renombrar la columna 'dirección' a 'direccion' si existe
            if 'dirección' in df.columns:
                df.rename(columns={'dirección': 'direccion'}, inplace=True)
            
            # Seleccionar las columnas deseadas
            columnas_deseadas = ['direccion', 'longitud', 'latitud']
            df_seleccionado = df.loc[:, columnas_deseadas]
            
            # Asegurarse de que las columnas longitud y latitud sean de tipo float
            df_seleccionado['longitud'] = df_seleccionado['longitud'].astype(float)
            df_seleccionado['latitud'] = df_seleccionado['latitud'].astype(float)
            
            # Crear una columna de geometría a partir de longitud y latitud
            df_seleccionado.loc[:, 'geom'] = df_seleccionado.apply(lambda row: WKTElement(f'POINT({row.longitud} {row.latitud})', srid=4326), axis=1)
            
            # Guardar el DataFrame en un archivo CSV en el directorio 'modificados'
            archivo_csv = os.path.join('modificados', f'{os.path.splitext(archivo)[0]}.csv')
            df_seleccionado.to_csv(archivo_csv, index=False)
            
            # Imprimir el DataFrame
            print(f"DataFrame del archivo: {archivo} guardado como {os.path.basename(archivo_csv)}")
            print(df_seleccionado)
            print("\n")

# Directorio donde se encuentran los archivos .xlsx
directorio_archivos = '../metadata/descargados'

# Llamar a la función para procesar los archivos
procesar_archivos(directorio_archivos)