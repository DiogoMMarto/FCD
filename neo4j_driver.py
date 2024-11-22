from concurrent.futures import ThreadPoolExecutor, as_completed
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "example123456789"
database = "neo4j"

driver = GraphDatabase.driver(uri, auth=(username, password))

def insert_node(tx, node_data):
    # Cypher query to create a node with its properties
    query = """
    MERGE (n:Page {number: $number})
    SET n.category = $category,
        n.date = $date,
        n.length = $length,
        n.mime = $mime,
        n.path = $path,
        n.status = $status,
        n.timestamp = $timestamp,
        n.title = $title,
        n.url = $url
    RETURN n
    """
    # Execute the query with node data
    tx.run(query, **node_data)

def insert_connections(tx, source_number, target_numbers):
    # Cypher query to create relationships
    for target_number in target_numbers:
        query = """
        MATCH (source:Page {number: $source_number})
        MERGE (target:Page {number: $target_number})
        MERGE (source)-[:LINKS_TO]->(target)
        """
        # Execute the query for each connection
        tx.run(query, source_number=source_number, target_number=target_number)

def add_page_to_neo4j(node_data,_driver = None):
    if _driver is None:
        _driver = driver
    with _driver.session() as session:
        # Insert the node
        session.execute_write(insert_node, node_data)
        # Insert its connections (relationships)
        session.execute_write(insert_connections, node_data['number'], node_data['connections'])

def add_all_pages_to_neo4h(nodes_data):
    i = 0
    with driver.session(database=database) as session:
        for node_data in nodes_data:
            i += 1; print("\rProgress: {}/{}".format(i, len(nodes_data)), end="")
            session.execute_write(insert_node, node_data)
    print()
    i = 0
    with driver.session(database=database) as session:
        for node_data in nodes_data:
            i += 1; print("\rProgress: {}/{}".format(i, len(nodes_data)), end="")
            session.execute_write(insert_connections, node_data['number'], node_data['connections'])
    print()
