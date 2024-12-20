from datetime import datetime
from neo4j import GraphDatabase
from flask import current_app, g
import functools
from website.helper import Node , NodeA

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
WHERE n.number <> 1787457
WITH n, count(*) AS c
ORDER BY c DESC
LIMIT 200
WITH collect(n.number) as cc
MATCH (n) -- (m) 
WHERE n.number in cc and m.number in cc
RETURN n, collect(m.number) as connections, count(*) as c order by c desc LIMIT 10
"""
@functools.cache
def first_graph():
    driver = get_driver()
    with driver.session() as session:
        q = session.run(query=QUERY_F)
        # convert to Node class
        return [Node(x["n"], x["connections"]) for x in q]

QUERY_N = """
MATCH (n)--(m)--(p)
WHERE n.number = $node_id AND p.number in $nodes_id
RETURN m , collect(p.number) as connections LIMIT 100
"""
def neighbors(node_id, nodes_id):
    driver = get_driver()
    with driver.session() as session:
        q = session.run(
            query=QUERY_N,
            node_id=node_id,
            nodes_id=nodes_id,
        )

        return [Node(x["m"],x["connections"]) for x in q]

QUERY_A = """
MATCH (n:Category)-[a:CONNECTED_TO]-(m:Category) RETURN n , collect(m.uniqueNumber) as connections , collect(m.name + ": " + toString(a.count)) as counts LIMIT 25
"""
def agg_graph():
    driver = get_driver()
    with driver.session() as session:
        q = session.run(query=QUERY_A)
        return [NodeA(x["n"], x["connections"], x["counts"]) for x in q]
    
def safe_query(query: str):
    qs = query.split(" ")
    for q in qs:
        if q.lower() in ["delete", "drop", "create","set","merge","remove","detach","alter","add"]:
            return False
    return True

def query_graph(query):
    driver = get_driver()
    with driver.session() as session:
        if not safe_query(query):
            return []
        q = session.run(query=query)
        return [Node(x["n"], x["connections"]) for x in q]

@functools.cache
def query_line(query):
    driver = get_driver()
    with driver.session() as session:
        if not safe_query(query):
            return []
        q = session.run(query=query)
        q = [{"x": x["x"], "y": x["y"]} for x in q if x["x"] and x["y"]]
        q = sorted(q, key=lambda x: datetime.strptime(x["x"], "%d/%m/%Y"))
        return q
    
def query_hist(query):
    driver = get_driver()
    with driver.session() as session:
        if not safe_query(query):
            print("Not safe")
            return []
        q = session.run(query=query)
        q = [{"x": x["x"], "y": x["y"]} for x in q if x["x"] and x["y"]]
        q = sorted(q, key=lambda x: datetime.strptime(x["x"], "%d/%m/%Y"))
        return q

def init_db(app):
    get_driver()
    app.teardown_appcontext(close_driver)

