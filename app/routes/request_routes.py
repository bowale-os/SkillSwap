from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User, Skill, SwapRequest, RequestStatus, Swap, SkillName
from app.forms.make_swap import MakeSwapForm

request_bp = Blueprint('request', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@request_bp.route('/make-swap', methods=['POST'])
def make_swap():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    user_id = user.id
    
    form = MakeSwapForm()

    user_skills = db.session.execute(
        db.select(Skill).filter_by(user_id=user_id)
    ).scalars().all()

    other_skill_names = db.session.execute(
        db.select(SkillName)
    ).scalars().all()

    # Dynamically set SelectField choices for the swap form
    form.offered_skill_id.choices = [(skill.id, skill.skill_name.name) for skill in user_skills]
    form.desired_skill_name.choices = [(skill_name.id, skill_name.name) for skill_name in other_skill_names]

    if form.validate_on_submit():
        desired_skill_name = form.desired_skill_name.data
        offered_skill_id = form.offered_skill_id.data
        description = form.description.data or ""  # Handle empty description

        try:
            swap = Swap(desired_skill_name_id=desired_skill_name, offered_skill_id=offered_skill_id, description=description, user_id=user_id)
            db.session.add(swap)
            db.session.commit()
            flash("Your swap request has been added to the Swap-Stream!", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash(f"Some error occurred while creating your swap request. Please message admin.", "error")
            return redirect(url_for('dashboard.dashboard'))
        
        return redirect(url_for('dashboard.dashboard'))

    return redirect(url_for('dashboard.dashboard'))

@request_bp.route('/request_swap', methods=['GET', 'POST'])
def request_swap():
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
    if swap_request and swap_request.recipient_id == user.id:
        swap_request.status = RequestStatus.accepted
        db.session.commit()
    return redirect(url_for('dashboard.dashboard'))

@request_bp.route('/request/<int:request_id>/reject')
def reject_request(request_id):
    user = get_current_user()
    swap_request = db.session.get(SwapRequest, request_id)
    if swap_request and swap_request.recipient_id == user.id:
        swap_request.status = RequestStatus.rejected
        db.session.commit()
    return redirect(url_for('dashboard.dashboard'))

