import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from flask import Flask
from flask_socketio import SocketIO
from flask_migrate import Migrate
from dotenv import load_dotenv

from app.models import db
from .sockets import socketio, register_socket_events

load_dotenv()


def _normalize_database_uri(raw_uri: str | None) -> str | None:
    """Normalize database URI for SQLAlchemy/psycopg and ensure SSL in production.

    - Accepts DATABASE_URI or DATABASE_URL values
    - Converts postgres:// → postgresql+psycopg://
    - Ensures +psycopg driver is specified
    - Appends sslmode=require if missing
    """
    if not raw_uri:
        return None

    uri = raw_uri.strip()

    # Upgrade scheme
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg://", 1)
    elif uri.startswith("postgresql://"):
        uri = uri.replace("postgresql://", "postgresql+psycopg://", 1)

    # Parse and ensure sslmode=require
    parsed = urlparse(uri)
    query_params = dict(parse_qsl(parsed.query))
    if "sslmode" not in query_params:
        query_params["sslmode"] = "require"
    new_query = urlencode(query_params)
    normalized = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )
    return normalized


def create_app():
    app = Flask(__name__)

    # Configuration
    secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")
    database_uri = os.getenv("DATABASE_URI") or os.getenv("DATABASE_URL")
    database_uri = _normalize_database_uri(database_uri)

    app.config["SECRET_KEY"] = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Extensions
    db.init_app(app)
    Migrate(app, db)

    # Ensure models are imported before creating tables
    from . import models  # noqa: F401

    # Create tables automatically on startup if they don't exist
    with app.app_context():
        db.create_all()

    # Register routes (blueprints)
    from .routes import register_routes
    register_routes(app)

    # Register socket events AFTER app is ready
    register_socket_events(app)

    return app
