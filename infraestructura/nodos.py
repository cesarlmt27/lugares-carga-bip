import os
import pandas as pd

def combinar_csv(directorio):
    # Lista para almacenar los DataFrames
    dataframes = []

    # Iterar sobre los archivos en el directorio
    for archivo in os.listdir(directorio):
        if archivo.endswith('.csv'):
            # Leer el archivo CSV
            archivo_path = os.path.join(directorio, archivo)
            df = pd.read_csv(archivo_path)
            
            # Seleccionar las columnas deseadas
            columnas_deseadas = ['uuid', 'longitud', 'latitud']
            if all(col in df.columns for col in columnas_deseadas):
                df_seleccionado = df[columnas_deseadas]
                dataframes.append(df_seleccionado)
    
    # Concatenar todos los DataFrames
    df_concatenado = pd.concat(dataframes, ignore_index=True)
    
    # Guardar el DataFrame concatenado en un nuevo archivo CSV
    archivo_concatenado = 'nodos.csv'
    df_concatenado.to_csv(archivo_concatenado, index=False)
    
    print(f"Archivo concatenado guardado como {archivo_concatenado}")

# Directorio donde se encuentran los archivos CSV
directorio_modificados = 'modificados'

# Llamar a la función para combinar los archivos CSV
combinar_csv(directorio_modificados)