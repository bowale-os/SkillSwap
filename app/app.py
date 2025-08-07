from flask import Flask
from flask_socketio import SocketIO
from models import db
from routes import register_routes
from sockets import socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)

    # Import all models to ensure they are registered with SQLAlchemy
    from models import User, Skill, SkillName, Category, Swap, SwapRequest, DiscussRequest, SwapMessage, SwapConversation

    with app.app_context():
        db.create_all() 

    # Register blueprints
    register_routes(app)

    # Initialize SocketIO with the app
    socketio.init_app(app, cors_allowed_origins="*")  # add CORS if needed

    return app

if __name__ == '__main__':
    app = create_app()

    socketio.run(app, debug=True, port=8000)
