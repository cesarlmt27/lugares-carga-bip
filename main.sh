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
popd

echo "Finalización de la ejecución de scripts"

set +x

tail -F /dev/null