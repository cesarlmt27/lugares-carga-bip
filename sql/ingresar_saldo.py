import json
from datetime import datetime
import psycopg

def insertar_saldo(json_file_path, conn):
    query = """
    INSERT INTO saldo (numero_tarjeta, estado_contrato, saldo_tarjeta, fecha_saldo)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (numero_tarjeta) DO UPDATE
    SET estado_contrato = EXCLUDED.estado_contrato,
        saldo_tarjeta = EXCLUDED.saldo_tarjeta,
        fecha_saldo = EXCLUDED.fecha_saldo;
    """
    
    with open(json_file_path, 'r') as jsonfile:
        data = json.load(jsonfile)
        numero_tarjeta = data['numero_tarjeta']
        estado_contrato = data['estado_contrato']
        saldo_tarjeta = data['saldo_tarjeta']
        fecha_saldo = datetime.strptime(data['fecha_saldo'], "%d/%m/%Y %H:%M")
        
        with conn.cursor() as cur:
            cur.execute(query, (numero_tarjeta, estado_contrato, saldo_tarjeta, fecha_saldo))
        conn.commit()

if __name__ == "__main__":
    conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")
    insertar_saldo('../metadata/saldo_bip.json', conn)
    conn.close()
    print("Datos actualizados en la base de datos.")