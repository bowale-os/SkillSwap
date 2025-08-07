from . import socketio
from flask_socketio import emit, join_room, leave_room

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_room')
def handle_join(data):
    room = data.get('room')
    join_room(room)
    emit('status', {'msg': f'Joined room {room}'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data.get('room')
    message = data.get('message')
    emit('receive_message', {'message': message}, room=room)
