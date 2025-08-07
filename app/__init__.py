import os
from flask import Flask
from flask_socketio import SocketIO
from flask_migrate import Migrate
from dotenv import load_dotenv
from app.models import db

from .sockets import socketio, register_socket_events  # ← import from your sockets/__init__.py

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions
    db.init_app(app)
    Migrate(app, db)

    # Register routes (blueprints)
    from .routes import register_routes
    register_routes(app)

    # Register socket events AFTER app is ready
    register_socket_events(app)

    return app
