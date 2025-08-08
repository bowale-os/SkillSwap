from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app.models import db, User, DiscussRequest, SwapRequest, SwapConversation, SwapMessage, MessageType, SwapStatus, Swap
from datetime import datetime, timezone

chat_bp = Blueprint('chat', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@chat_bp.route('/chat/<string:request_id>', methods=['GET', 'POST'])
def chat(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    # Get the discuss request
    discuss_request = db.session.get(DiscussRequest, request_id)
    if not discuss_request:
        return "Discuss request not found", 404

    # Check if user is authorized to view this chat
    if user.id not in [discuss_request.sender_id, discuss_request.recipient_id]:
        return "You are not authorized to view this chat", 403

    # Get or create the conversation
    conversation = None
    if discuss_request.swap_conversation:
        conversation = db.session.get(SwapConversation, discuss_request.swap_conversation.id)
    
    if not conversation:
        # Create a swap conversation between the two users
        conversation = SwapConversation(
            swap_id=discuss_request.swap_id,
            sender_id=discuss_request.sender_id,
            recipient_id=discuss_request.recipient_id,
            discuss_request_id=discuss_request.id  # Link the conversation to the discuss request
        )
        db.session.add(conversation)
        
        discuss_request.swap_conversation_id = conversation.id
        db.session.commit()

    # Handle new message post
    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            # Determine recipient as "the other participant" in this conversation
            if user.id == conversation.sender_id:
                recipient_id = conversation.recipient_id
            else:
                recipient_id = conversation.sender_id

            message = SwapMessage(
                conversation_id=conversation.id,
                sender_id=user.id,
                recipient_id=recipient_id,
                content=content,
                type=MessageType.TEXT,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(message)
            db.session.commit()

    # Fetch all messages for the conversation
    messages = db.session.execute(
        db.select(SwapMessage).filter_by(conversation_id=conversation.id).order_by(SwapMessage.timestamp)
    ).scalars().all()

    return render_template(
        'chat-interface.html',
        conversation=conversation,
        messages=messages,
        discuss_request=discuss_request,
        user=user  # pass user for template logic
    )

@chat_bp.route('/accept_swap/<string:conversation_id>', methods=['POST'])
def accept_swap(conversation_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not authenticated'}), 401

    try:
        # Get the conversation
        conversation = db.session.get(SwapConversation, conversation_id)
        if not conversation:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404

        # Check if user is authorized to accept this swap
        if user.id not in [conversation.sender_id, conversation.recipient_id]:
            return jsonify({'success': False, 'error': 'Not authorized to accept this swap'}), 403

        # Set user's acceptance
        conversation.set_user_acceptance(user.id, True)
        
        # Check if both users have accepted
        if conversation.both_accepted:
            # Update swap status to completed
            swap = db.session.get(Swap, conversation.swap_id)
            if swap:
                swap.status = SwapStatus.completed
        
        db.session.commit()

        # Return current state
        return jsonify({
            'success': True,
            'user_accepted': True,
            'other_accepted': conversation.get_user_acceptance_status(
                conversation.recipient_id if user.id == conversation.sender_id else conversation.sender_id
            ),
            'both_accepted': conversation.both_accepted,
            'other_user_name': conversation.recipient.name if user.id == conversation.sender_id else conversation.sender.name
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error accepting swap: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while accepting the swap'}), 500

@chat_bp.route('/undo_accept_swap/<string:conversation_id>', methods=['POST'])
def undo_accept_swap(conversation_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not authenticated'}), 401

    try:
        # Get the conversation
        conversation = db.session.get(SwapConversation, conversation_id)
        if not conversation:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404

        # Check if user is authorized
        if user.id not in [conversation.sender_id, conversation.recipient_id]:
            return jsonify({'success': False, 'error': 'Not authorized'}), 403

        # Check if swap is already completed
        if conversation.both_accepted:
            return jsonify({'success': False, 'error': 'Cannot undo - swap already completed'}), 400

        # Undo user's acceptance
        conversation.set_user_acceptance(user.id, False)
        db.session.commit()

        return jsonify({
            'success': True,
            'user_accepted': False,
            'other_accepted': conversation.get_user_acceptance_status(
                conversation.recipient_id if user.id == conversation.sender_id else conversation.sender_id
            ),
            'both_accepted': False
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error undoing acceptance: {e}")
        return jsonify({'success': False, 'error': 'An error occurred'}), 500