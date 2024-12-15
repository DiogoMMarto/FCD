from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import INSERT
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "example123456789"
database = "neo4j"

driver = GraphDatabase.driver(uri, auth=(username, password))

INSERT_NODE_QUERY = """
MERGE (n:Page {number: $number})
SET n.category = $category,
    n.date = $date,
    n.path = $path,
    n.timestamp = $timestamp,
    n.title = $title,
    n.url = $url
RETURN n
"""

INSERT_CONNECTIONS_QUERY = """
MATCH (source:Page {number: $source_number})
MATCH (target:Page {number: $target_number})
MERGE (source)-[:LINKS_TO]->(target)
"""

def insert_node(tx, node_data):
    # Execute the query with node data
    tx.run(INSERT_NODE_QUERY, **node_data)

def insert_connections(tx, source_number, target_numbers):
    for target_number in target_numbers:
        tx.run(INSERT_CONNECTIONS_QUERY, source_number=source_number, target_number=target_number)

def add_page_to_neo4j(node_data,_driver = None):
    if _driver is None:
        _driver = driver
    with _driver.session() as session:
        insert_node(session, node_data)
        insert_connections(session, node_data['number'], node_data['connections'])

def add_all_pages_to_neo4h(nodes_data):
    i = 0
    # create index on node number
    with driver.session(database=database) as session:
        session.run("CREATE INDEX number_index FOR (n:Page) ON (n.number)")
    
    def batch_insert(nodes_data):
        with driver.session(database=database) as session:
            with session.begin_transaction() as tx:
                for node_data in nodes_data:
                    add_page_to_neo4j(node_data, tx)
                tx.commit()

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(batch_insert, nodes_data[i:i+100]) for i in range(0, len(nodes_data), 100)]
        for future in as_completed(futures):
            i += 100
            print(f"\r{i}/{len(nodes_data)}", end="")

    print("\nDone")