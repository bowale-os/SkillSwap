from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

def register_socket_events(app):
    from . import events  # import handlers to register them
    socketio.init_app(app)
