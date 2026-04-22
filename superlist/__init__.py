from flask import Flask
from .config import Config
from .extensions import db


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
