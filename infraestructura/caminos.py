import osmnx as ox
import psycopg

# Función para cargar los caminos en PostGIS
def cargar_caminos_postgis(edges, conn):
    query_insertar_caminos = """
    INSERT INTO caminos (osm_id, highway, name, geom)
    VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));
    """
    
    with conn.cursor() as cur:
        for _, row in edges.iterrows():
            # Verificar si osm_id es una lista o un solo valor, y usar el primer valor si es una lista
            osm_id = row['osmid']
            if isinstance(osm_id, list):
                osm_id = osm_id[0]  # Tomar el primer valor de la lista
            
            line = row['geometry'].wkt  # Convertir la geometría a WKT
            
            # Ejecutar la inserción con osm_id corregido
            cur.execute(query_insertar_caminos, (osm_id, row.get('highway'), row.get('name'), line))
        conn.commit()

# Cargar la red caminable desde OpenStreetMap
def descargar_red_caminable():
    print("Descargando la red caminable para Santiago, Chile...")
    graph = ox.graph_from_place('Santiago, Chile', network_type='walk')
    print("Red caminable descargada con éxito.")
    
    # Convertir a GeoDataFrame para obtener las aristas
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    return edges

# Guardar la red caminable en un archivo GeoJSON
def guardar_caminos_geojson(edges):
    print("Guardando los caminos en caminos_santiago.geojson...")
    edges.to_file("caminos_santiago.geojson", driver="GeoJSON")
    print("Caminos guardados en caminos_santiago.geojson.")

# Conectar a la base de datos PostGIS
def conectar_postgis():
    return psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=postgis port=5432")

# Ejecutar el proceso completo
def main():
    conn = conectar_postgis()
    
    # Descargar y guardar la red caminable
    edges = descargar_red_caminable()
    guardar_caminos_geojson(edges)
    
    # Cargar los caminos en PostGIS
    print("Cargando los caminos en PostGIS...")
    cargar_caminos_postgis(edges, conn)
    print("Caminos cargados en PostGIS con éxito.")
    
    conn.close()

if __name__ == "__main__":
    main()
