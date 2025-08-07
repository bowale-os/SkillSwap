from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models import db, User, Skill, SwapRequest, RequestStatus
from app.forms.make_swap import MakeSwapForm

request_bp = Blueprint('request', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@request_bp.route('/request_swap', methods=['GET', 'POST'])
def make_swap():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    form = MakeSwapForm()
    
    # Populate form fields
    form.offered_skill_id.choices = [(str(skill.id), skill.name.name) for skill in user.skills]
    form.desired_skill_name.choices = [(skill.name.name, skill.name.name) for skill in Skill.query.filter(Skill.user_id != user.id).all()]

    if form.validate_on_submit():
        desired_skill_name = form.desired_skill_name.data
        offered_skill_id = form.offered_skill_id.data
        description = form.description.data

        desired_skill = Skill.query.join(User).join(Skill.name).filter(
            Skill.name.has(name=desired_skill_name),
            Skill.user_id != user.id
        ).first()

        if not desired_skill:
            return "Desired skill not found", 404

        new_request = SwapRequest(
            sender_id=user.id,
            receiver_id=desired_skill.user_id,
            desired_skill_id=desired_skill.id,
            offered_skill_id=offered_skill_id,
            description=description,
            status=RequestStatus.PENDING
        )
        db.session.add(new_request)
        db.session.commit()

        return redirect(url_for('dashboard.dashboard'))

    return render_template('request_swap.html', form=form)

@request_bp.route('/request/<int:request_id>/accept')
def accept_request(request_id):
    user = get_current_user()
    swap_request = db.session.get(SwapRequest, request_id)
    if swap_request and swap_request.receiver_id == user.id:
        swap_request.status = RequestStatus.ACCEPTED
        db.session.commit()
    return redirect(url_for('dashboard.dashboard'))

@request_bp.route('/request/<int:request_id>/reject')
def reject_request(request_id):
    user = get_current_user()
    swap_request = db.session.get(SwapRequest, request_id)
    if swap_request and swap_request.sender_id == user.id:
        swap_request.status = RequestStatus.REJECTED
        db.session.commit()
    return redirect(url_for('dashboard.dashboard'))

