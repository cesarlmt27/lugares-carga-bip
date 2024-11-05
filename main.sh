#!/bin/bash

set -x

pushd infraestructura
python3 datosgob.py
python3 nodos.py
python3 caminos.py
popd

pushd metadata
python3 cajeros.py
python3 informacion.py
python3 saldo_bip.py
popd

pushd amenazas
python3 atropellos.py
python3 feriados.py
python3 robos.py
popd

pushd sql
python3 ejecutar_sql.py
python3 seed.py
popd

set +x

tail -F /dev/null