from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import db, User, Skill, SwapRequest, DiscussRequest, SkillName, Category, Swap, SwapStatus, RequestStatus, SwapConversation
from app.forms.add_skill import AddSkillForm
from app.forms.make_swap import MakeSwapForm
from sqlalchemy import select

dashboard_bp = Blueprint('dashboard', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@dashboard_bp.route('/')
def home():
    user = get_current_user()
    if user:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    user_id = user.id

    form = AddSkillForm()
    swap_form = MakeSwapForm()

    skill_names = db.session.execute(db.select(SkillName)).scalars().all()
    categories = db.session.execute(db.select(Category)).scalars().all()

    form.name.choices = [(sn.id, sn.name) for sn in skill_names]
    form.category.choices = [(cat.id, cat.name) for cat in categories]

    user_skills = db.session.execute(
        db.select(Skill).filter_by(user_id=user_id)
    ).scalars().all()

    user_skill_name_ids = [skill.skill_name_id for skill in user_skills if skill.skill_name_id]

    print(f"User skill_name_ids: {user_skill_name_ids}")
    print(f"User skills count: {len(user_skills)}")

    # Just all open or in_discussion swaps for testing
    open_swaps = db.session.execute(
        db.select(Swap).filter(
            Swap.status.in_([SwapStatus.open, SwapStatus.in_discussion])
        )
    ).scalars().all()
    print(f"Total open/in_discussion swaps: {len(open_swaps)}")

    # Subquery: Check if user already sent a swap request for that swap
    subquery = (
        db.select(SwapRequest.id)
        .filter(
            SwapRequest.swap_id == Swap.id,
            SwapRequest.sender_id == user_id
        )
        .correlate(Swap)
    )

    # Main query with all filters (your original query)
    unrequested_swaps = db.session.execute(
        db.select(Swap).filter(
            (Swap.user_id != user_id),
            (Swap.status.in_([SwapStatus.open, SwapStatus.in_discussion])),
            (~db.exists(subquery)),
            (Swap.desired_skill_name_id.in_(user_skill_name_ids))
        )
    ).scalars().all()

    print(f"Unrequested swaps count: {len(unrequested_swaps)}")
    for swap in unrequested_swaps:
        print(f"Swap id: {swap.id}, Offered skill: {swap.offered_skill.skill_name.name}, Desired skill: {swap.desired_skill_name.name}")

    # Prepare swap_form choices
    other_skill_names = db.session.execute(db.select(SkillName)).scalars().all()
    swap_form.desired_skill_name.choices = [(sn.id, sn.name) for sn in other_skill_names]
    swap_form.offered_skill_id.choices = [(skill.id, skill.skill_name.name) for skill in user_skills]

    sent_swap_requests = db.session.execute(db.select(SwapRequest).filter_by(sender_id=user_id)).scalars().all()
    received_swap_requests = db.session.execute(db.select(SwapRequest).filter_by(recipient_id=user_id)).scalars().all()

    sent_discuss_requests = db.session.execute(db.select(DiscussRequest).filter_by(sender_id=user_id)).scalars().all()
    received_discuss_requests = db.session.execute(db.select(DiscussRequest).filter_by(recipient_id=user_id)).scalars().all()

    # Check which swaps already have swap requests sent by the current user (for swap stream)
    swap_request_exists = {}
    for swap in unrequested_swaps:
        existing_swap_request = db.session.execute(
            select(SwapRequest).where(
                SwapRequest.sender_id == user_id,
                SwapRequest.swap_id == swap.id
            )
        ).scalar_one_or_none()
        swap_request_exists[swap.id] = existing_swap_request is not None

    # Check which received swap requests already have discuss requests (for received requests section)
    discuss_request_exists = {}
    for swap_request in received_swap_requests:
        existing_discuss = db.session.execute(
            select(DiscussRequest).where(
                DiscussRequest.sender_id == user_id,
                DiscussRequest.recipient_id == swap_request.sender_id,
                DiscussRequest.swap_id == swap_request.swap_id
            )
        ).scalar_one_or_none()
        discuss_request_exists[swap_request.id] = existing_discuss is not None

    return render_template(
        'dashboard.html',
        form=form,
        swap_form=swap_form,
        current_user=user,
        skills=user_skills,
        swaps=unrequested_swaps,
        sent_swap_requests=sent_swap_requests or None,
        received_swap_requests=received_swap_requests or None,
        sent_discuss_requests=sent_discuss_requests or None,
        received_discuss_requests=received_discuss_requests or None,
        swap_request_exists=swap_request_exists,
        discuss_request_exists=discuss_request_exists
    )

@dashboard_bp.route('/send_swap_request/<string:swap_id>', methods=['POST'])
def send_swap_request(swap_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    user_id = user.id
    sender_skill_id = request.form.get('sender_skill_id')
    
    swap = db.get_or_404(Swap, swap_id)
    recipient_id = swap.user_id
    recipient_skill_id = swap.offered_skill_id
    
    try:
        swap_request = SwapRequest(
            swap_id=swap_id,
            sender_id=user_id,
            sender_skill_id=sender_skill_id,
            recipient_id=recipient_id,
            recipient_skill_id=recipient_skill_id
        )
        db.session.add(swap_request)
        db.session.commit()
        flash("Swap request was made successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash(f"Swap request was not created! {e}", "error")
        return redirect(url_for('dashboard.dashboard'))

    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/discuss_swap/<string:request_id>', methods=['GET'])
def discuss_swap_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    user_id = user.id
    corr_swap_request = db.get_or_404(SwapRequest, request_id)

    # Check if the user is the recipient of the original swap request
    if corr_swap_request.recipient_id != user_id:
        flash("You are not authorized to start this discussion.", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    # Check if a DiscussRequest already exists
    existing_discuss = db.session.execute(
        select(DiscussRequest).where(
            DiscussRequest.sender_id == user_id,
            DiscussRequest.recipient_id == corr_swap_request.sender_id,
            DiscussRequest.swap_id == corr_swap_request.swap_id
        )
    ).scalar_one_or_none()
    
    if existing_discuss:
        flash("Discussion already initiated.", "info")
        return redirect(url_for('dashboard.view_discuss_request', request_id=existing_discuss.id))

    # Create the DiscussRequest
    discuss_request = DiscussRequest(
        sender_id=user_id,
        recipient_id=corr_swap_request.sender_id,
        swap_id=corr_swap_request.swap_id,
        sender_skill_id=corr_swap_request.recipient_skill_id,
        recipient_skill_id=corr_swap_request.sender_skill_id,
        status=RequestStatus.pending
    )
    
    db.session.add(discuss_request)
    db.session.commit()

    flash("Discussion request sent successfully!", "success")
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/view_discuss_request')
def view_discuss_request():
    # TODO: Implement view discuss request functionality
    pass

@dashboard_bp.route('/accept_discuss_request/<string:request_id>')
def accept_discuss_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        discuss_request = db.get_or_404(DiscussRequest, request_id)
        
        # Check if user is the recipient of this discuss request
        if discuss_request.recipient_id != user.id:
            flash("You are not authorized to accept this discuss request.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        
        # Accept the discuss request
        discuss_request.accept()
        
        # Create a swap conversation between the two users
        swap_conversation = SwapConversation(
            swap_id=discuss_request.swap_id,
            sender_id=discuss_request.recipient_id,
            recipient_id=discuss_request.sender_id
        )
        db.session.add(swap_conversation)
        
        # Link the discuss request to the conversation
        discuss_request.swap_conversation_id = swap_conversation.id
        
        db.session.commit()
        
        flash("Discuss request accepted successfully! The swap is now in discussion.", "success")
        
        return render_template('chat_interface.html', discuss_request=discuss_request, swap_conversation=swap_conversation)
        
    except Exception as e:
        db.session.rollback()
        print(f"Error accepting discuss request: {e}")
        flash("An error occurred while accepting the discuss request.", "error")
        return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/reject_discuss_request/<string:request_id>', methods=['POST'])
def reject_discuss_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        discuss_request = db.get_or_404(DiscussRequest, request_id)
        
        # Check if user is the recipient of this discuss request
        if discuss_request.recipient_id != user.id:
            flash("You are not authorized to reject this discuss request.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        
        # Reject the discuss request
        discuss_request.reject()
        db.session.commit()
        
        flash("Discuss request rejected successfully.", "info")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error rejecting discuss request: {e}")
        flash("An error occurred while rejecting the discuss request.", "error")
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/withdraw_discuss_request')
def withdraw_discuss_request():
    # TODO: Implement withdraw discuss request functionality
    pass

@dashboard_bp.route('/delete_discuss_request/<string:request_id>', methods=['GET'])
def delete_discuss_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    try:
        discuss_request = db.get_or_404(DiscussRequest, request_id)
        
        # Check if user is authorized to delete this discuss request
        if discuss_request.sender_id != user.id and discuss_request.recipient_id != user.id:
            flash("You are not authorized to delete this discuss request.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        
        # Use the cancel method to update status instead of hard deleting
        discuss_request.cancel()
        db.session.commit()
        
        flash("Discuss request cancelled successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cancelling discuss request: {e}")
        flash("An error occurred while cancelling the discuss request.", "error")
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/delete_swap_request/<string:request_id>', methods=['GET'])
def delete_swap_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    try:
        swap_request = db.get_or_404(SwapRequest, request_id)
        
        # Check if user is authorized to delete this swap request
        if swap_request.sender_id != user.id and swap_request.recipient_id != user.id:
            flash("You are not authorized to delete this swap request.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        
        # Use the cancel method to update status instead of hard deleting
        swap_request.cancel()
        db.session.commit()
        
        flash("Swap request cancelled successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cancelling swap request: {e}")
        flash("An error occurred while cancelling the swap request.", "error")
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/edit_skill_desc/<string:skill_id>', methods=['GET', 'POST'])
def edit_skill_desc(skill_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    new_desc = request.form.get('new-desc')
    print(new_desc)
    try:
        skill = db.get_or_404(Skill, skill_id)
        if skill:
            db.session.execute(
                db.select(Skill).filter_by(id=skill_id)
            )
            skill.description = new_desc
            db.session.commit()
        else:
            flash("Skill was not found.")
            return redirect(url_for('dashboard.dashboard'))
    except Exception as e:
        print(f"encountered this error, {e}")
        flash("Please reach out to admin")
        return redirect(url_for('dashboard.dashboard'))
    
    flash("Skill was edited successfully.")
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/delete_skill/<string:skill_id>', methods=['GET'])
def delete_skill(skill_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    user_id = user.id

    try:
        skill = db.get_or_404(Skill, skill_id)
        if skill.user_id != user_id:
            flash("You are not authorized to delete this skill!", "error")
            return redirect(url_for('dashboard.dashboard'))
        
        # Delete related SwapRequest records
        related_requests = db.session.execute(
            db.select(SwapRequest).filter(
                (SwapRequest.sender_skill_id == skill_id) | (SwapRequest.recipient_skill_id == skill_id)
            )
        ).scalars().all()
        
        for request in related_requests:
            db.session.delete(request)
        
        # Delete the skill
        db.session.delete(skill)
        db.session.commit()
        flash("Skill and all related swap requests deleted successfully!", "success")
    except Exception as e:
        print(f"Encountered error while trying to delete Skill: {e}")
        flash(f"Skill was not deleted! Please reach out to admin.", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/accept_swap_request/<string:request_id>', methods=['POST'])
def accept_swap_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        swap_request = db.get_or_404(SwapRequest, request_id)
        
        # Check if user is the recipient of this swap request
        if swap_request.recipient_id != user.id:
            flash("You are not authorized to accept this swap request.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        
        # Accept the swap request
        swap_request.accept()
        db.session.commit()
        
        flash("Swap request accepted successfully! The swap is now in discussion.", "success")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error accepting swap request: {e}")
        flash("An error occurred while accepting the swap request.", "error")
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/reject_swap_request/<string:request_id>', methods=['POST'])
def reject_swap_request(request_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        swap_request = db.get_or_404(SwapRequest, request_id)
        
        # Check if user is the recipient of this swap request
        if swap_request.recipient_id != user.id:
            flash("You are not authorized to reject this swap request.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        
        # Reject the swap request
        swap_request.reject()
        db.session.commit()
        
        flash("Swap request rejected successfully.", "info")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error rejecting swap request: {e}")
        flash("An error occurred while rejecting the swap request.", "error")
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/update_swap_statuses', methods=['POST'])
def update_swap_statuses():
    """Update all swap statuses - useful for maintenance"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        # Update all swap statuses
        Swap.update_all_statuses(db.session)
        flash("All swap statuses have been updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating swap statuses: {e}")
        flash("An error occurred while updating swap statuses.", "error")
    
    return redirect(url_for('dashboard.dashboard'))
