from . import socketio
from flask_socketio import emit

@socketio.on('send_notification')
def handle_send_notification(data):
    target_user_id = data.get('target_user_id')
    notification_type = data.get('type')
    message = data.get('message')

    emit('receive_notification', {
        'type': notification_type,
        'message': message
    }, room=f'user_{target_user_id}')
