import osmnx as ox
import psycopg
import geopandas as gpd

def descargar_red_caminable(lugar):
    # Descargar la red caminable para la Región Metropolitana
    print(f"Descargando la red caminable para {lugar}...")
    G = ox.graph_from_place(lugar, network_type='walk')
    
    # Convertir a GeoDataFrame
    edges = ox.graph_to_gdfs(G, nodes=False)
    print("Red caminable descargada con éxito.")
    
    # Guardar en archivo GeoJSON
    print(f"Guardando los caminos en caminos_{lugar.replace(' ', '_')}.geojson...")
    edges.to_file(f"caminos_{lugar.replace(' ', '_')}.geojson", driver="GeoJSON")
    print(f"Caminos guardados en caminos_{lugar.replace(' ', '_')}.geojson.")
    
    return edges

def cargar_caminos_postgis(edges, conn):
    query_insertar_caminos = """
    INSERT INTO caminos (osm_id, highway, name, geom)
    VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326))
    ON CONFLICT (osm_id) DO NOTHING;
    """
    
    with conn.cursor() as cur:
        for _, row in edges.iterrows():
            osm_id = row['osmid'][0] if isinstance(row['osmid'], list) else row['osmid']
            geom = row['geometry']
            line = geom.wkt  # Convertir la geometría a Well-Known Text (WKT)
            cur.execute(query_insertar_caminos, (osm_id, row.get('highway'), row.get('name'), line))
        conn.commit()
    print("Caminos cargados en PostGIS con éxito.")

def main():
    # Definir el lugar
    lugar = "Región Metropolitana de Santiago, Chile"
    
    # Descargar la red caminable
    edges = descargar_red_caminable(lugar)
    
    # Conectar a la base de datos PostGIS
    conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=postgis port=5432")
    
    # Cargar los caminos en PostGIS
    cargar_caminos_postgis(edges, conn)
    
    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    main()
