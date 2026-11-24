
import os
from flask import Flask, render_template

from .database import init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get(
            "SECRET_KEY",
            "aurelia-development-secret-change-before-deployment"
        )
    )

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    init_db(app)

    # Register authentication routes.
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Register customer review routes.
    from .routes.reviews import reviews_bp
    app.register_blueprint(reviews_bp)

    # Register staff dashboard routes.
    from .routes.staff import staff_bp
    app.register_blueprint(staff_bp)

    # Register customer spending routes.
    from .routes.spending import spending_bp
    app.register_blueprint(spending_bp)

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
