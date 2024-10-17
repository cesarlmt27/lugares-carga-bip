#!/bin/bash

cd sql

python3 ejecutar_sql.py

python3 seed.py

cd ..

cd infraestructura

python3 caminos.py