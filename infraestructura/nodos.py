import os
import pandas as pd

def procesar_archivos(directorio):
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
            
            # Renombrar la columna 'DIRECCIÓN' a 'DIRECCION' si existe
            if 'DIRECCIÓN' in df.columns:
                df.rename(columns={'DIRECCIÓN': 'DIRECCION'}, inplace=True)
            
            # Seleccionar las columnas deseadas
            columnas_deseadas = ['DIRECCION', 'LONGITUD', 'LATITUD']
            df_seleccionado = df[columnas_deseadas]
            
            # Imprimir el DataFrame
            print(f"DataFrame del archivo: {archivo}")
            print(df_seleccionado)
            print("\n")

# Directorio donde se encuentran los archivos .xlsx
directorio_archivos = '../metadata/archivos'

# Llamar a la función para procesar los archivos
procesar_archivos(directorio_archivos)