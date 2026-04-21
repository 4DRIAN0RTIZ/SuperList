import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///superlist.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
