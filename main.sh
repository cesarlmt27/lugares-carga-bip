#!/bin/bash

set -x

echo "Inicio de la ejecución de scripts"

# Ejecutar scripts de infraestructura/nodos
pushd infraestructura/nodos
python3 datosgob.py
python3 nodos.py
popd

# Ejecutar scripts de infraestructura/aristas
# pushd infraestructura/aristas
# python3 aristas.py
# popd

# Ejecutar scripts de metadata
pushd metadata
python3 cajeros.py
python3 informacion.py
python3 saldo_bip.py 123456
popd

# Ejecutar scripts de amenazas
pushd amenazas
python3 atropellos.py
python3 feriados.py
# python3 robos.py
popd

# Ejecutar scripts SQL
pushd sql
python3 ejecutar_sql.py crear_tablas.sql
python3 ingresar_saldo.py
python3 seed.py
python3 ejecutar_sql.py post_seed.sql
python3 ruta.py

python3 ejecutar_sql.py probabilidades/proba_atropellos.sql
python3 ejecutar_sql.py probabilidades/proba_cajeros.sql
python3 ejecutar_sql.py probabilidades/proba_feriados.sql
python3 meta.py
popd

echo "Finalización de la ejecución de scripts"

# Ejecutar la API
pushd sitio_web
python3 app.py
popd

set +x
