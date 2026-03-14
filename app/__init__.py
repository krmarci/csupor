import os
from urllib.parse import quote_plus

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"


def _build_database_uri() -> str:
    """Build DB URI from DATABASE_URL or MYSQL_* environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_db = os.getenv("MYSQL_DATABASE", "csupor")

    auth = quote_plus(mysql_user)
    if mysql_password:
        auth = f"{auth}:{quote_plus(mysql_password)}"

    return f"mysql+pymysql://{auth}@{mysql_host}:{mysql_port}/{mysql_db}"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = _build_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes  # noqa: F401

    routes.init_routes(app)

    with app.app_context():
        db.create_all()

    return app
