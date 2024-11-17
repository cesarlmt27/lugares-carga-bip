from flask import Flask, jsonify
import psycopg
from datetime import date

app = Flask(__name__)

def get_db_connection():
    conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")
    return conn

@app.route('/feriado/hoy', methods=['GET'])
def get_feriado_hoy():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feriados WHERE fecha = %s", (date.today(),))
    feriado = cur.fetchone()
    cur.close()
    conn.close()

    if feriado:
        feriado_dict = {
            'id': feriado[0],
            'nombre': feriado[1],
            'comentarios': feriado[2],
            'fecha': feriado[3],
            'irrenunciable': feriado[4],
            'tipo': feriado[5]
        }
        return jsonify(feriado_dict)
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/feriado/<fecha>', methods=['GET'])
def get_feriado_por_fecha(fecha):
    try:
        fecha = date.fromisoformat(fecha)
    except ValueError:
        return jsonify({'error': 'Bad request. Format: YYYY-MM-DD.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feriados WHERE fecha = %s", (fecha,))
    feriado = cur.fetchone()
    cur.close()
    conn.close()

    if feriado:
        feriado_dict = {
            'id': feriado[0],
            'nombre': feriado[1],
            'comentarios': feriado[2],
            'fecha': feriado[3],
            'irrenunciable': feriado[4],
            'tipo': feriado[5]
        }
        return jsonify(feriado_dict)
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/saldo/<numero_tarjeta>', methods=['GET'])
def get_saldo(numero_tarjeta):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM saldo WHERE numero_tarjeta = %s", (numero_tarjeta,))
    saldo = cur.fetchone()
    cur.close()
    conn.close()

    if saldo:
        saldo_dict = {
            'numero_tarjeta': saldo[0],
            'estado_contrato': saldo[1],
            'saldo_tarjeta': saldo[2],
            'fecha_saldo': saldo[3]
        }
        return jsonify(saldo_dict)
    else:
        return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")