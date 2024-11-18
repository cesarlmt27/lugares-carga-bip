FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app
COPY main.sh /app

RUN apt-get update && \
    apt-get install -y wget osm2pgsql postgresql-client gdal-bin && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./main.sh"]