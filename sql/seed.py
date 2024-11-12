from datetime import datetime
import json
import psycopg
import csv
import subprocess

def insertar_nodos(csv_file_path, conn):
    query = """
    INSERT INTO nodos (uuid, longitud, latitud, geom)
    VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """
    
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with conn.cursor() as cur:
            for row in reader:
                uuid = row['uuid']
                longitud = float(row['longitud'])
                latitud = float(row['latitud'])
                cur.execute(query, (uuid, longitud, latitud, longitud, latitud))

def insertar_rutas(chile, rm):
    # Importar datos de OSM a la base de datos
    subprocess.run(["osm2pgsql", "-d", "postgres", "-U", "postgres", "-H", "db", "--create", "--slim", "-G", chile], check=True)

    # Importar límites administrativos a la base de datos
    subprocess.run(["ogr2ogr", "-f", "PostgreSQL", "PG:dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432", rm, "-nln", "rm_santiago"], check=True)


def insertar_informacion(csv_file_path, conn):
    query = """
    INSERT INTO informacion (uuid, codigo, entidad, direccion, comuna, horario)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with conn.cursor() as cur:
            for row in reader:
                uuid = row['uuid']
                codigo = str(row['codigo'])
                entidad = row['entidad']
                direccion = row['direccion']
                comuna = row['comuna']
                horario = row['horario']
                cur.execute(query, (uuid, codigo, entidad, direccion, comuna, horario))

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

def insertar_saldo(json_file_path, conn):
    query = """
    INSERT INTO saldo (numero_tarjeta, estado_contrato, saldo_tarjeta, fecha_saldo)
    VALUES (%s, %s, %s, %s);
    """
    
    with open(json_file_path, 'r') as jsonfile:
        data = json.load(jsonfile)
        numero_tarjeta = data['numero_tarjeta']
        estado_contrato = data['estado_contrato']
        saldo_tarjeta = data['saldo_tarjeta']
        fecha_saldo = datetime.strptime(data['fecha_saldo'], "%d/%m/%Y %H:%M")
        
        with conn.cursor() as cur:
            cur.execute(query, (numero_tarjeta, estado_contrato, saldo_tarjeta, fecha_saldo))



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
            
            # Convertir a float los campos numéricos
            cur.execute(query, (
                float(props['dmcs']), 
                float(props['robos']), 
                float(props['robos_f']), 
                float(props['robos_v']), 
                float(props['nivel_dmcs']), 
                float(props['nivel_robo']), 
                float(props['nivel_rf']), 
                float(props['nivel_rv']), 
                float(props['size']), 
                geom
            ))



# Conectar a la base de datos
conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")

insertar_nodos('../infraestructura/nodos/nodos.csv', conn)

insertar_rutas('../infraestructura/aristas/chile-latest.osm.pbf', '../infraestructura/aristas/rm_santiago.geojson')

insertar_informacion('../metadata/informacion.csv', conn)

with open('../metadata/cajeros.geojson', 'r', encoding='utf-8') as f:
    datos_cajeros = json.load(f)
insertar_cajeros(datos_cajeros, conn)

insertar_saldo('../metadata/saldo_bip.json', conn)

with open('../amenazas/atropellos.geojson', 'r', encoding='utf-8') as f:
    datos_atropellos = json.load(f)
insertar_atropellos(datos_atropellos, conn)

with open('../amenazas/feriados.json', 'r', encoding='utf-8') as f:
    datos_feriados = json.load(f)
insertar_feriados(datos_feriados, conn)

with open('../amenazas/robos.json', 'r', encoding='utf-8') as f:
    datos_robos = json.load(f)
insertar_robos(datos_robos, conn)

# Cerrar la conexión
conn.commit()
conn.close()