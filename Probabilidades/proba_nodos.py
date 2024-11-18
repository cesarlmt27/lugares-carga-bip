import pandas as pd 
from shapely.geometry import Point, Polygon

# Cargar los datos de probabilidad_fallas.csv y nodos.csv
probabilidad_fallas_df = pd.read_csv("../Probabilidades/probabilidad_fallas.csv")  # Cargar el CSV de probabilidad de fallas
probabilidad_falla_atropello = pd.read_csv("../Probabilidades/nodos_con_probabilidad_atropellos.csv")  # Cargar el CSV de probabilidad de atropellos
nodos_df = pd.read_csv("../infraestructura/nodos/nodos.csv")  # Cargar el CSV de nodos

# Función para crear un polígono a partir de las coordenadas de un hexágono
def crear_poligono(coordenadas):
    return Polygon(coordenadas)

# Función para verificar si un nodo está dentro de un polígono y obtener la probabilidad de falla
def obtener_probabilidad_falla(nodo, hexagonos_poligonos):
    point = Point(nodo['longitud'], nodo['latitud'])
    for hexagono, probabilidad in hexagonos_poligonos:
        if hexagono.contains(point):
            return probabilidad
    return 0.0  # Si no está dentro de ningún hexágono, devolver 0.0

# Crear una lista de polígonos a partir de las coordenadas de los hexágonos y asociarles la probabilidad
hexagonos_poligonos = []

# Agrupar por 'id' para crear un polígono para cada hexágono y asociar la probabilidad
for _, group in probabilidad_fallas_df.groupby('id'):
    coordenadas_hexagono = group[['longitude', 'latitude']].values.tolist()
    probabilidad = group['probabilidad'].iloc[0]  # Asumimos que todos los vértices de un hexágono tienen la misma probabilidad
    hexagono = crear_poligono(coordenadas_hexagono)
    hexagonos_poligonos.append((hexagono, probabilidad))

# Función para obtener la probabilidad de atropellos para cada nodo
def obtener_probabilidad_atropellos(nodo, atropellos_df):
    # Buscar el nodo en el DataFrame de atropellos y obtener la probabilidad
    nodo_atropello = atropellos_df[atropellos_df['uuid'] == nodo['uuid']]
    if not nodo_atropello.empty:
        return nodo_atropello['probabilidad_atropellos'].iloc[0]
    return 0.0  # Si no se encuentra el nodo en los atropellos, devolver 0.0

# Obtener la probabilidad de falla para cada nodo
nodos_df['probabilidad'] = nodos_df.apply(lambda nodo: obtener_probabilidad_falla(nodo, hexagonos_poligonos), axis=1)

# Obtener la probabilidad de atropellos para cada nodo
nodos_df['probabilidad_atropellos'] = nodos_df.apply(lambda nodo: obtener_probabilidad_atropellos(nodo, probabilidad_falla_atropello), axis=1)

# Sumar las probabilidades de falla y atropellos
nodos_df['probabilidad_total'] = nodos_df['probabilidad'] + nodos_df['probabilidad_atropellos']

# Seleccionar solo las columnas 'uuid', 'longitud', 'latitud' y 'probabilidad_total'
nodos_resultado_df = nodos_df[['uuid', 'longitud', 'latitud', 'probabilidad_total']]

# Guardar el resultado en un nuevo archivo CSV
nodos_resultado_df.to_csv('nodos_con_probabilidad_total.csv', index=False)

print("Archivo de nodos con las probabilidades de falla y atropellos guardado.")
