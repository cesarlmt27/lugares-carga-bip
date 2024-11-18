import psycopg
import sys


def check_connectivity(conn, start_node, end_node):
    """
    Check if the start and end nodes are within the same connected component.
    """
    query = """
    WITH components AS (
        SELECT *
        FROM pgr_connectedComponents(
            'SELECT osm_id AS id, source, target, cost FROM rm_line'
        )
    )
    SELECT c1.component
    FROM components c1
    JOIN components c2 ON c1.component = c2.component
    WHERE c1.node = %s AND c2.node = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (start_node, end_node))
        result = cur.fetchone()
        return result is not None  # True if connected



def fetch_candidate_nodes(conn):
    """
    Fetch nodes within Ñuñoa and Providencia with scores based on threats and conveniences.
    """
    query = """
    WITH region_nodes AS (
        SELECT id AS node_id, the_geom
        FROM rm_line_vertices_pgr
        WHERE ST_Within(the_geom, (SELECT ST_Union(wkb_geometry)
                                   FROM rm_santiago
                                   WHERE comuna IN ('Providencia', 'Ñuñoa')))
    ),
    threats AS (
        SELECT rn.node_id, 
               COALESCE(SUM(a.probabilidad), 0) AS threat_penalty
        FROM region_nodes rn
        LEFT JOIN atropello_comuna a
        ON ST_DWithin(rn.the_geom, a.coordenadas, 100)
        GROUP BY rn.node_id
    ),
    conveniences AS (
        SELECT rn.node_id, 
               COALESCE(SUM(1.0 / c.probabilidad), 0) AS convenience_bonus
        FROM region_nodes rn
        LEFT JOIN cajeros_comuna c
        ON ST_DWithin(rn.the_geom, c.coordenadas, 200)
        GROUP BY rn.node_id
    ),
    final_scores AS (
        SELECT 
            rn.node_id,
            ST_AsText(rn.the_geom) AS geometry,
            COALESCE(t.threat_penalty, 0) AS threat_penalty,
            COALESCE(c.convenience_bonus, 0) AS convenience_bonus,
            COALESCE(c.convenience_bonus, 0) - COALESCE(t.threat_penalty, 0) AS probabilidad
        FROM region_nodes rn
        LEFT JOIN threats t ON rn.node_id = t.node_id
        LEFT JOIN conveniences c ON rn.node_id = c.node_id
    )
    SELECT 
        node_id, geometry, probabilidad, threat_penalty, convenience_bonus
    FROM final_scores
    ORDER BY probabilidad DESC;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def create_shortest_path_table(conn, start_node, end_node):
    """
    Create the shortest path table using pgr_dijkstra.
    """
    query = """
    CREATE TABLE IF NOT EXISTS meta_ruta AS
    SELECT roads.*
    FROM rm_line AS roads
    JOIN pgr_dijkstra(
        'SELECT osm_id AS id, source, target, cost FROM rm_line',
        %s, %s, false
    ) AS route ON roads.osm_id = route.edge;
    """
    with conn.cursor() as cur:
        cur.execute(query, (start_node, end_node))
        conn.commit()
        print("meta_ruta table created.")


def main():
    try:
        conn = psycopg.connect("dbname=postgres user=postgres password=kj2aBv6f33cZ host=db port=5432")
        print("Connected to the database.")
    except psycopg.OperationalError as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

    input_longitude, input_latitude = -70.6012037, -33.4433545

    # Find the nearest start node from rm_line_vertices_pgr
    nearest_query = """
    SELECT id AS node_id
    FROM rm_line_vertices_pgr
    ORDER BY ST_Distance(the_geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
    LIMIT 1;
    """
    with conn.cursor() as cur:
        cur.execute(nearest_query, (input_longitude, input_latitude))
        start_node = cur.fetchone()[0]
    print(f"Nearest Start Node: {start_node}")

    # Fetch candidate nodes within Ñuñoa and Providencia
    print("Fetching candidate nodes...")
    nodes = fetch_candidate_nodes(conn)
    if not nodes:
        print("No candidate nodes found.")
        conn.close()
        sys.exit(1)

    print(f"Fetched {len(nodes)} nodes within Ñuñoa and Providencia.")

    # Iterate through candidate nodes to find a connected destination
    for node in nodes:
        end_node = node[0]
        print(f"Testing connectivity for End Node: {end_node}")
        if check_connectivity(conn, start_node, end_node):
            print(f"Nodes {start_node} and {end_node} are connected.")
            create_shortest_path_table(conn, start_node, end_node)
            print(f"Optimal Node: ID={end_node}, Geometry={node[1]}, Probability={node[2]}")
            break
        else:
            print(f"Nodes {start_node} and {end_node} are not connected. Testing next candidate...")
    else:
        print("No connected destination nodes found.")
    
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()

