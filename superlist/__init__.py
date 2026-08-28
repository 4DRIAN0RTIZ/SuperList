from flask import Flask

from . import models  # noqa: F401  (import so migrations/autogenerate see the models)
from .blueprints.main import bp as main_bp
from .cli import register_cli
from .config import get_config
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config or get_config())

    db.init_app(app)
    # render_as_batch lets Alembic rewrite tables on SQLite, which has no
    # real ALTER TABLE for dropping/altering columns and constraints.
    migrate.init_app(app, db, render_as_batch=True)

    app.register_blueprint(main_bp)
    register_cli(app)

    return app
