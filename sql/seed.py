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


def insertar_cajeros(datos_json, conn):
    query = """
    INSERT INTO cajeros (atm, tipo, estado, institucion, administrador, direccion, comuna, ciudad, region,
                        tipo_local, local, horario_lunes, horario_martes, horario_miercoles, horario_jueves,
                        horario_viernes, horario_sabado, horario_domingo, tipo_horario, longitud, latitud, coordenadas)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """
    
    with conn.cursor() as cur:
        for banco in datos_json:
            cur.execute(query, (
                banco['ATM'], banco['TIPO'], banco['ESTADO'], banco['INSTITUCION'], banco['ADMINISTRADOR'], 
                banco['DIRECCION'], banco['COMUNA'], banco['CIUDAD'], banco['REGION'], banco['TIPO LOCAL'], 
                banco['LOCAL'], banco['H. LUNES'], banco['H. MARTES'], banco['H. MIERCOLES'], banco['H. JUEVES'], 
                banco['H. VIERNES'], banco['H. SABADO'], banco['H. DOMINGO'], banco['TIPO HORARIO'], 
                banco['LONGITUD'], banco['LATITUD'], banco['LONGITUD'], banco['LATITUD']
            ))
        

def insertar_feriados(datos_json, conn):
    query = """
    INSERT INTO feriados (nombre, comentarios, fecha, irrenunciable, tipo, leyes)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    with conn.cursor() as cur:
        for feriado in datos_json:
            leyes = json.dumps(feriado['leyes'])  # Convertir a JSON
            irrenunciable = True if feriado['irrenunciable'] == "1" else False
            cur.execute(query, (
                feriado['nombre'], feriado['comentarios'], feriado['fecha'], irrenunciable, feriado['tipo'], leyes
            ))


def insertar_robos(datos_geojson, conn):
    query = """
    INSERT INTO robos (feature_id, dmcs, robos, robos_f, robos_v, nivel_dmcs, nivel_robo, nivel_rf, nivel_rv, size, coordenadas)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """
    
    with conn.cursor() as cur:
        for feature in datos_geojson['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates'][0] 
            
            cur.execute(query, (
                feature['id'],
                props['dmcs'], props['robos'], props['robos_f'], props['robos_v'], 
                props['nivel_dmcs'], props['nivel_robo'], props['nivel_rf'], props['nivel_rv'], props['size'],
                coords[0], coords[1]
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
