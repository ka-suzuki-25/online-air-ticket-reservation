# app/reservation/routes/__init__.py
from .airport import airport_bp
from .auth import auth_bp
from .reviews import reviews_bp
from .spending import spending_bp
from .staff import staff_bp

BLUEPRINTS = (auth_bp, reviews_bp, staff_bp, spending_bp, airport_bp)


def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)