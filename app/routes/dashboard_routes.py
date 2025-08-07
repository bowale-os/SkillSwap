from flask import Blueprint, render_template, session, redirect, url_for
from app.models import db, User, Skill, SwapRequest, DiscussRequest, SkillName, Category, Swap, SwapStatus, RequestStatus
from app.forms.add_skill import AddSkillForm
from app.forms.make_swap import MakeSwapForm

dashboard_bp = Blueprint('dashboard', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@dashboard_bp.route('/')
def home():
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
        received_discuss_requests=received_discuss_requests or None
    )
