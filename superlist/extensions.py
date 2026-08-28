import os
import sqlite3

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record):
    """Harden every new SQLite connection.

    SQLite ships with foreign keys disabled and rollback-journal mode by
    default. WAL plus enforced foreign keys is the sane baseline for a
    small web app: real referential integrity and non-blocking reads
    while a write is in flight.
    """
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return

    cursor = dbapi_connection.cursor()
    # Alembic batch migrations rebuild referenced tables; SQLite blocks that
    # while foreign keys are enforced. env.py sets this flag for migrations.
    if not os.environ.get("SUPERLIST_ALEMBIC"):
        cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
