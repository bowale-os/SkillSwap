from flask import Flask
from flask_socketio import SocketIO
from models import db
from routes import routes_bp
from sockets import socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        db.create_all() 

    # Register blueprints
    app.register_blueprint(routes_bp)

    # Initialize SocketIO with the app
    socketio.init_app(app, cors_allowed_origins="*")  # add CORS if needed

    return app

if __name__ == '__main__':
    app = create_app()

    socketio.run(app, debug=True, port=8000)
