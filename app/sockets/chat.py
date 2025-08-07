from . import socketio
from flask_socketio import emit, join_room

@socketio.on('join_chat')
def handle_join_chat(data):
    room = data.get('room')
    username = data.get('username')
    join_room(room)
    emit('chat_announcement', {'msg': f'{username} has joined the chat'}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    room = data.get('room')
    message = data.get('message')
    sender = data.get('sender')
    emit('receive_message', {'sender': sender, 'message': message}, room=room)
