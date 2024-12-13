from neo4j import GraphDatabase
from flask import current_app, g
import functools
from website.helper import Node

def get_driver():
    if "driver" not in g:
        g.driver = GraphDatabase.driver(
            current_app.config["NEO4J_URI"],
            auth=( current_app.config["NEO4J_USER"], current_app.config["NEO4J_PASSWORD"] ),
        )
    return g.driver

def close_driver():
    driver = g.pop("driver", None)
    if driver is not None:
        driver.close()

QUERY_F = """
MATCH (n)--()
WHERE n.timestamp > 20220908110000
WITH n, count(*) AS c
ORDER BY c DESC
LIMIT 10
WITH collect(n.number) as cc
MATCH (n) -- (m) 
WHERE n.number in cc and m.number in cc
RETURN n, collect(m.number) as connections, count(*) as c order by c desc
"""
@functools.cache
def first_graph():
    driver = get_driver()
    with driver.session() as session:
        q = session.run(query=QUERY_F)
        # convert to Node class
        return [Node(x["n"], x["connections"]) for x in q]

def init_db(app):
    get_driver()
    app.teardown_appcontext(close_driver)

