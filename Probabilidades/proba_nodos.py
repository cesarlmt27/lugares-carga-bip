import pandas as pd
from shapely.geometry import Point, Polygon

# Cargar los datos de probabilidad_fallas.csv y nodos.csv
probabilidad_fallas_df = pd.read_csv("../Probabilidades/probabilidad_fallas.csv")  # Cargar el CSV correctamente
nodos_df = pd.read_csv("../infraestructura/nodos/nodos.csv")  # Cargar el CSV correctamente

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
    probabilidad_falla = group['probabilidad_falla'].iloc[0]  # Asumimos que todos los vértices de un hexágono tienen la misma probabilidad
    hexagono = crear_poligono(coordenadas_hexagono)
    hexagonos_poligonos.append((hexagono, probabilidad_falla))

# Obtener la probabilidad de falla para cada nodo
nodos_df['probabilidad_falla'] = nodos_df.apply(lambda nodo: obtener_probabilidad_falla(nodo, hexagonos_poligonos), axis=1)

# Guardar el resultado en un nuevo archivo CSV
nodos_df.to_csv('nodos_con_probabilidad_falla.csv', index=False)

print("Archivo de nodos con la probabilidad de falla guardado.")
