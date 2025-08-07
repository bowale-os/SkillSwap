from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Run the app with SocketIO support on port 8000
    socketio.run(app, debug=True, port=8000, allow_unsafe_werkzeug=True)
