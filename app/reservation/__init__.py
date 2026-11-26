
import os
from flask import Flask, render_template

from . import database
from .routes import register_blueprints



def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"]
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # close the MySQL connection after each request
    database.init_app(app)

    # Register routes.
    register_blueprints(app)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return {
            "status": "running",
            "application": "Aurelia Airways"
        }

    return app
