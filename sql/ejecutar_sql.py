import psycopg
import sys

# Función para ejecutar un archivo .sql
def execute_sql_file(file_path):
    # Leer el archivo .sql
    with open(file_path, 'r') as file:
        sql = file.read()

    # Dividir el contenido del archivo en sentencias individuales
    statements = sql.split(';')

    # Ejecutar cada sentencia y hacer commit
    for statement in statements:
        if statement.strip():  # Ignorar sentencias vacías
            cur.execute(statement)
            conn.commit()

conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")
cur = conn.cursor()

# Obtener el path del archivo .sql desde los argumentos de la línea de comandos
if len(sys.argv) != 2:
    print("Uso: python ejecutar_sql.py <path_del_archivo_sql>")
    sys.exit(1)

sql_file_path = sys.argv[1]

# Llamar a la función con la ruta del archivo .sql
execute_sql_file(sql_file_path)

cur.close()
conn.close()