"""
Create a Flask application and call related functions to initialize the project.
Related functions such as registering routes and initializing database.
"""
import os

from flask import Flask
from dotenv import dotenv_values
from dirs import ROOT_DIR
from flask_cors import CORS


def create_app(test_config=None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'rb_system.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        if os.path.exists(f'{ROOT_DIR}/.env'):
            config = dotenv_values(f'{ROOT_DIR}/.env')
            app.config.from_mapping(config)
        else:
            # register env variables for deployment
            app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        from api.routes import register_routes
        from api.db import init_database
        from api.commands.server import register_commands

        init_database(app)
        register_routes(app)
        register_commands(app)

    CORS(app, origins=["*"])
    return app
