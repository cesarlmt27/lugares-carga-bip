import subprocess

# Descargar datos de OSM
subprocess.run(["wget", "http://download.geofabrik.de/south-america/chile-latest.osm.pbf", "-O", "chile-latest.osm.pbf"], check=True)

# Descargar límites administrativos de la RM
subprocess.run(["wget", "https://raw.githubusercontent.com/caracena/chile-geojson/refs/heads/master/13.geojson", "-O", "rm_santiago.geojson"], check=True)