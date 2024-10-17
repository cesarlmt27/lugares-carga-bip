import osmnx as ox
import psycopg
import geopandas as gpd

# Paso 1: Descargar la red caminable de OpenStreetMap usando osmnx
def descargar_red_caminable(lugar):
    print(f"Descargando la red caminable para {lugar}...")
    G = ox.graph_from_place(lugar, network_type='walk')
    nodes, edges = ox.graph_to_gdfs(G)
    print("Red caminable descargada con éxito.")
    return edges

# Paso 2: Guardar los caminos en un archivo GeoJSON (opcional)
def guardar_geojson(edges, filename='caminos.geojson'):
    print(f"Guardando los caminos en {filename}...")
    edges.to_file(filename, driver='GeoJSON')
    print(f"Caminos guardados en {filename}.")

# Paso 3: Cargar los datos de caminos en PostGIS
def cargar_caminos_postgis(edges, conn):
    print("Cargando los caminos en PostGIS...")
    
    # Crear una tabla en PostGIS
    query_crear_tabla = """
    CREATE TABLE IF NOT EXISTS caminos (
        id SERIAL PRIMARY KEY,
        osm_id BIGINT,
        highway TEXT,
        name TEXT,
        geom GEOMETRY(LineString, 4326)
    );
    """
    
    with conn.cursor() as cur:
        cur.execute(query_crear_tabla)
    
        # Insertar los datos de los caminos en PostGIS
        query_insertar_caminos = """
        INSERT INTO caminos (osm_id, highway, name, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));
        """
    
        for idx, row in edges.iterrows():
            line = row['geometry'].wkt
            cur.execute(query_insertar_caminos, (row['osmid'], row.get('highway'), row.get('name'), line))
    
    conn.commit()
    print("Caminos cargados exitosamente en PostGIS.")

# Paso 4: Conectar a la base de datos
def conectar_postgis():
    return psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=postgis port=5432")

# Ejecución
lugar = "Santiago, Chile"
edges = descargar_red_caminable(lugar)
guardar_geojson(edges, "caminos_santiago.geojson")

# Conectar a la base de datos y cargar los caminos en PostGIS
conn = conectar_postgis()
cargar_caminos_postgis(edges, conn)
conn.close()
