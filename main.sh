#!/bin/bash

set -x

echo "Inicio de la ejecución de scripts"

# Ejecutar scripts de infraestructura
pushd infraestructura
python3 datosgob.py
python3 nodos.py
python3 caminos.py
popd

# Ejecutar scripts de metadata
pushd metadata
python3 cajeros.py
python3 informacion.py
python3 saldo_bip.py
popd

# Ejecutar scripts de amenazas
pushd amenazas
python3 atropellos.py
python3 feriados.py
# python3 robos.py
popd

# Ejecutar scripts SQL
pushd sql
python3 ejecutar_sql.py
python3 seed.py
popd

echo "Finalización de la ejecución de scripts"

set +x

tail -F /dev/null