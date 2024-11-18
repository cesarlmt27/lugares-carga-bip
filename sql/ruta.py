import psycopg
import json

# Conectar a la base de datos
conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")

def find_nearest_node(conn, lon, lat):
    """
    Find the nearest node in `rm_comuna_vertices_pgr` to the given coordinates.
    """
    query = f"""
    SELECT id AS node_id, 
           ST_AsText(the_geom) AS geometry, 
           ST_Distance(the_geom, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)) AS distance
    FROM rm_comuna_vertices_pgr
    ORDER BY distance
    LIMIT 1;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchone()
        if result:
            node_id, geometry, distance = result
            geom_parts = geometry.replace("POINT(", "").replace(")", "").split(" ")
            longitude, latitude = float(geom_parts[0]), float(geom_parts[1])
            return {"node_id": node_id, "longitude": longitude, "latitude": latitude, "distance": distance}
    return None

def find_top_5_clustered_nodes(conn, longitude, latitude):
    """
    Find the top 5 nearest nodes to the given coordinates using ST_ClusterDBSCAN.
    """
    query = f"""
    WITH params AS (
        SELECT 
            ST_SetSRID(ST_MakePoint({longitude}, {latitude}), 4326) AS origin,
            100 AS eps,
            5 AS max_nodes
    ),
    clustered_nodes AS (
        SELECT 
            id, geom, longitud, latitud,
            ST_ClusterDBSCAN(geom, eps := (SELECT eps FROM params), minpoints := 1) OVER () AS cluster_id,
            ST_Distance(geom, (SELECT origin FROM params)) AS distance
        FROM nodos
    ),
    top_5_nodes AS (
        SELECT id AS node_id, geom, longitud, latitud, distance
        FROM clustered_nodes
        ORDER BY distance
        LIMIT (SELECT max_nodes FROM params)
    )
    SELECT node_id, longitud, latitud, ST_AsText(geom) AS geometry, distance
    FROM top_5_nodes
    ORDER BY distance;
    """
    try:
        with conn.cursor() as cur:
            # Execute the query
            cur.execute(query)
            result = cur.fetchall()
            
            # Parse and return the results
            return [
                {"node_id": row[0], "longitude": row[1], "latitude": row[2], "geometry": row[3], "distance": row[4]}
                for row in result
            ]
    except Exception as e:
        print(f"Error finding clustered nodes: {e}")
        return []


def find_closest_nodes(conn, top_5_nodes):
    """
    Find the closest nodes in `rm_comuna_vertices_pgr` for each node in the top 5 nodes list.
    """
    # Construct the VALUES clause dynamically
    values_clause = ", ".join(
        f"({node['node_id']}, ST_SetSRID(ST_MakePoint({node['longitude']}, {node['latitude']}), 4326))"
        for node in top_5_nodes
    )
    
    query = f"""
    WITH input_nodes (node_id, geom) AS (
        VALUES {values_clause}
    )
    SELECT DISTINCT ON (nodes.node_id) 
        nodes.node_id AS input_node_id,
        rcvp.id AS closest_node_id,
        ST_Distance(rcvp.the_geom, nodes.geom) AS distance
    FROM input_nodes AS nodes
    JOIN rm_comuna_vertices_pgr AS rcvp
    ON ST_DWithin(rcvp.the_geom, nodes.geom, 1000)
    ORDER BY nodes.node_id, distance;
    """
    
    try:
        with conn.cursor() as cur:
            # Execute the query
            cur.execute(query)
            result = cur.fetchall()

            # Return the parsed results
            return [
                {"input_node_id": row[0], "closest_node_id": row[1], "distance": row[2]}
                for row in result
            ]
    except Exception as e:
        print(f"Error finding closest nodes: {e}")
        return []


def calculate_route_costs_using_coordinates(conn, nearest_longitude, nearest_latitude, closest_nodes):
    """
    Calculate the shortest route costs from the nearest coordinates to the destination nodes using pgr_dijkstra.
    """
    # Extract destination IDs from the closest nodes
    destination_ids = [node["closest_node_id"] for node in closest_nodes]
    
    if not destination_ids:
        print("No destination nodes provided.")
        return []

    # Construct destination array for the query
    destination_array = ", ".join(map(str, destination_ids))
    
    query = f"""
    WITH origin_node AS (
        SELECT id AS node_id
        FROM rm_comuna_vertices_pgr
        ORDER BY ST_Distance(the_geom, ST_SetSRID(ST_MakePoint({nearest_longitude}, {nearest_latitude}), 4326))
        LIMIT 1
    ),
    destinations AS (
        SELECT UNNEST(ARRAY[{destination_array}]) AS dest_id
    ),
    routes AS (
        SELECT 
            d.dest_id AS destination,
            SUM((pgr).cost) AS total_cost
        FROM destinations d
        CROSS JOIN LATERAL (
            SELECT * 
            FROM pgr_dijkstra(
                'SELECT osm_id AS id, source, target, cost FROM rm_comuna',
                (SELECT node_id FROM origin_node),
                d.dest_id,
                false
            )
        ) AS pgr
        GROUP BY d.dest_id
    )
    SELECT destination AS closest_node_id, total_cost
    FROM routes
    ORDER BY total_cost ASC;
    """
    
    try:
        with conn.cursor() as cur:
            # Execute the query
            cur.execute(query)
            result = cur.fetchall()

            # Parse and return the results
            return [{"closest_node_id": row[0], "total_cost": row[1]} for row in result]
    except Exception as e:
        print(f"Error calculating route costs: {e}")
        return []


def insert_route(conn, source_node_id, target_node_id):
    """
    Insert or update a route in the `ruta` table.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS ruta (
        id SERIAL PRIMARY KEY,
        source_id INTEGER NOT NULL,
        target_id INTEGER NOT NULL,
        geometry GEOMETRY(LINESTRING, 4326)
    );

    WITH routes AS (
        SELECT edge AS osm_id
        FROM pgr_dijkstra(
            'SELECT osm_id AS id, source, target, cost FROM rm_comuna',
            {source_node_id},
            {target_node_id},
            false
        )
    ),
    route_geometry AS (
        SELECT 
            rm.osm_id, 
            rm.way AS geometry
        FROM rm_comuna rm
        JOIN routes r ON rm.osm_id = r.osm_id
    ),
    full_route AS (
        SELECT 
            ST_LineMerge(ST_Union(geometry))::GEOMETRY(LineString, 4326) AS geometry
        FROM route_geometry
    )
    INSERT INTO ruta (source_id, target_id, geometry)
    SELECT {source_node_id}, {target_node_id}, geometry
    FROM full_route
    WHERE geometry IS NOT NULL; -- Ensure geometry is valid
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            print(f"Route inserted successfully between {source_node_id} and {target_node_id}.")
    except Exception as e:
        print(f"Error inserting route: {e}")


# Main execution flow
input_longitude, input_latitude = -70.6012037, -33.4433545

nearest_node = find_nearest_node(conn, input_longitude, input_latitude)
if nearest_node:
    top_5_nodes = find_top_5_clustered_nodes(conn, nearest_node["longitude"], nearest_node["latitude"])
    closest_nodes = find_closest_nodes(conn, top_5_nodes)
    route_costs = calculate_route_costs_using_coordinates(conn, nearest_node["longitude"], nearest_node["latitude"], closest_nodes)
    if route_costs:
        target_node = route_costs[0]
        insert_route(conn, nearest_node["node_id"], target_node["closest_node_id"])


# Cerrar la conexión
conn.commit()
conn.close()

