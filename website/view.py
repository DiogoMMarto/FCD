from operator import le
from flask import (
    Blueprint, Response, app, flash, g, redirect, render_template, request, session, url_for
)

import website.db as db
from website.helper import node_list_to_json

bp = Blueprint('view', __name__, url_prefix='')

@bp.route('/')
def index():

    nodes = db.first_graph()

    return render_template('index.html', nodes=nodes)

@bp.route('/first_graph')
def get_first_graph():  
    nodes = db.first_graph()

    return Response(node_list_to_json(nodes), mimetype='application/json')