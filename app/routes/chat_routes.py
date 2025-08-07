from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models import db, User, SwapRequest, SwapConversation, SwapMessage, MessageType
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@chat_bp.route('/chat/<int:request_id>', methods=['GET', 'POST'])
def chat(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    # Get the swap request
    swap_request = db.session.get(SwapRequest, request_id)
    if not swap_request:
        return "Swap request not found", 404

    # Find or create the conversation
    conversation = SwapConversation.query.filter_by(swap_request_id=swap_request.id).first()
    if not conversation:
        conversation = SwapConversation(swap_request_id=swap_request.id)
        db.session.add(conversation)
        db.session.commit()

    # Handle new message post
    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            # Determine the recipient as the other user in the swap
            recipient_id = swap_request.requester_id if user.id != swap_request.requester_id else swap_request.receiver_id

            message = SwapMessage(
                conversation_id=conversation.id,
                sender_id=user.id,
                recipient_id=recipient_id,
                content=content,
                type=MessageType.TEXT,
                timestamp=datetime.utcnow()
            )
            db.session.add(message)
            db.session.commit()

    # Fetch all messages for the conversation
    messages = SwapMessage.query.filter_by(conversation_id=conversation.id).order_by(SwapMessage.timestamp).all()

    return render_template(
        'chat.html',
        conversation=conversation,
        messages=messages,
        swap_request=swap_request,
        user=user  # pass user for template logic
    )
