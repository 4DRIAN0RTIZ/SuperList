import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'superlist.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # pool_pre_ping recycles connections dropped by the OS; the timeout keeps
    # a blocked SQLite writer from hanging a request forever.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {"timeout": 15},
    }


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    def __init__(self):
        if self.SECRET_KEY == "dev-insecure-key-change-me":
            raise RuntimeError("SECRET_KEY must be set in the environment for production")


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config():
    name = os.environ.get("FLASK_ENV", "development").strip().lower()
    return _CONFIGS.get(name, DevelopmentConfig)
