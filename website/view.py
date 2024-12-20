import json
from flask import (
    Blueprint, Response, app, flash, g, redirect, render_template, request, session, url_for
)

import website.db as db
from website.helper import node_list_to_json, to_plot

bp = Blueprint('view', __name__, url_prefix='')

@bp.route('/')
def index():

    nodes = db.first_graph()

    return render_template('index.html', nodes=nodes)

@bp.route('/first_graph')
def get_first_graph():  
    nodes = db.first_graph()
    print(node_list_to_json(nodes))
    return Response(node_list_to_json(nodes), mimetype='application/json')

@bp.route('/graph')
def graph():
    query = request.args.get('query')
    if query is None:
        return redirect(url_for('view.index'))
    nodes = db.query_graph(query)
    return Response(node_list_to_json(nodes), mimetype='application/json')

# get the neighbors of a node using node.id and and ids of the nodes in graph
@bp.route('/neighbors/<int:node_id>', methods=['POST'])
def get_neighbors(node_id):
    nodes_id = json.loads(request.data)
    nodes = db.neighbors(node_id, nodes_id)

    return Response(node_list_to_json(nodes), mimetype='application/json')

# agg_graph
@bp.route('/agg_graph')
def get_agg_graph():
    nodes = db.agg_graph()

    return Response(node_list_to_json(nodes), mimetype='application/json')

@bp.route('/aggregrate')
def aggregrate():
    return render_template('index_agg.html')

@bp.route('/plot')
def plot():
    return render_template('index_graph.html')

@bp.route('/plots')
def api_plot():
    # /plots?type=line&query=match%20(n)%20return%20n.date%20as%20x,%20count(*)%20as%20y%20order%20by%20x%20desc
    query = request.args.get('query')
    type = request.args.get('type')
    if type == 'hist':
        points = db.query_hist(query)
    else:
        points = db.query_line(query)

    return Response(to_plot(points), mimetype='application/json')