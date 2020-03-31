import os

from flask import Flask
from flask_cors import CORS

from .commands import dump_data
from config import config

def create_app(config_name):
    app = Flask(__name__)
    CORS(app, origins='*')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    app.cli.add_command(dump_data)

    from app.models import db
    db.init_app(app)

    from app.api import api
    app.register_blueprint(api)

    return app

