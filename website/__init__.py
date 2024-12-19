import os 
from flask import Flask, send_from_directory
from flask_cors import CORS  # Import Flask-CORS
from . import db
from . import view

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        NEO4J_URI=os.getenv('NEO4J_URI', 'neo4j://localhost:7687'),
        NEO4J_USER=os.getenv('NEO4J_USER', 'neo4j'),
        NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD', 'example123456789'),
        NEO4J_DATABASE=os.getenv('NEO4J_DATABASE', 'neo4j')
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
   
    app.register_blueprint(view.bp)


    CORS(app, resources={r"/website/*": {"origins": "*"}})
   # register folder "../.cache" to serve files staticly
    @app.route('/website/<path:path>')
    def send_website(path):
        return send_from_directory('../.cache', path)

    @app.route('/ping')
    def hello():
        return "pong"

    return app
