import json
import psycopg

def insertar_atropellos(datos_geojson, conn):
    query = """
    INSERT INTO atropellos (año, claseaccid, cod_regi, region, comuna, cod_zona, zona, calle_uno, calle_dos,
                            intersecci, numero, ruta, ubicacion_1, siniestros, fallecidos, graves, menos_grav,
                            leves, ilesos, coordenadas)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """
    
    with conn.cursor() as cur:
        for feature in datos_geojson['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates'][0]
            cur.execute(query, (
                props['Año'], props['Claseaccid'], props['Cód_Regi'], props['Región'], props['Comuna'], 
                props['Cód_Zona'], props['Zona'], props['Calle_Uno'], props['Calle_Dos'], 
                props['Intersecci'], props['Número'], props['Ruta'], props['Ubicaci_1'], props['Siniestros'], 
                props['Fallecidos'], props['Graves'], props['Menos_grav'], props['Leves'], props['Ilesos'], coords[0], coords[1]
            ))


def insertar_cajeros(cajeros_geojson, conn):
    query = """
    INSERT INTO cajeros (atm, institucion, direccion, comuna, ciudad, region, categoria, estado, coordenadas)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """
    
    with conn.cursor() as cur:
        for feature in cajeros_geojson['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            cur.execute(query, (
                props.get('ATM'), 
                props.get('institucion'), 
                props.get('direccion'), 
                props.get('comuna'), 
                props.get('ciudad'), 
                props.get('region'), 
                props.get('categoria'), 
                props.get('estado'),
                coords[0],  # Longitud
                coords[1]   # Latitud
            ))
        

def insertar_feriados(datos_json, conn):
    query = """
    INSERT INTO feriados (nombre, comentarios, fecha, irrenunciable, tipo)
    VALUES (%s, %s, %s, %s, %s);
    """
    
    with conn.cursor() as cur:
        for feriado in datos_json:
            irrenunciable = True if feriado['irrenunciable'] == "1" else False
            cur.execute(query, (
                feriado['nombre'], 
                feriado['comentarios'], 
                feriado['fecha'], 
                irrenunciable, 
                feriado['tipo']
            ))

def insertar_robos(datos_geojson, conn):
    query = """
    INSERT INTO robos (dmcs, robos, robos_f, robos_v, nivel_dmcs, nivel_robo, nivel_rf, nivel_rv, size, geom)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_Multi(ST_GeomFromGeoJSON(%s)), 4326));
    """
    
    with conn.cursor() as cur:
        for feature in datos_geojson['features']:
            props = feature['properties']
            geom = json.dumps(feature['geometry'])  # Convertir la geometría a formato GeoJSON
            
            # Ejecutar la consulta para insertar los datos
            cur.execute(query, (
                int(props['dmcs']), 
                int(props['robos']), 
                int(props['robos_f']), 
                int(props['robos_v']), 
                int(props['nivel_dmcs']), 
                int(props['nivel_robo']), 
                int(props['nivel_rf']), 
                int(props['nivel_rv']), 
                int(props['size']), 
                geom
            ))



# Conectar a la base de datos
conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=postgis port=5432")

# Cargar los datos desde archivos
with open('../amenazas/atropellos.geojson', 'r', encoding='utf-8') as f:
    datos_atropellos = json.load(f)
insertar_atropellos(datos_atropellos, conn)

with open('../metadata/cajeros.geojson', 'r', encoding='utf-8') as f:
    datos_cajeros = json.load(f)
insertar_cajeros(datos_cajeros, conn)

with open('../amenazas/feriados.json', 'r', encoding='utf-8') as f:
    datos_feriados = json.load(f)
insertar_feriados(datos_feriados, conn)

with open('../amenazas/robos.json', 'r', encoding='utf-8') as f:
    datos_robos = json.load(f)
insertar_robos(datos_robos, conn)

conn.commit()
conn.close()
