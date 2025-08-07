from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.forms.add_skill import AddSkillForm
from app.models import db, User, Skill, SkillName, Category

skill_bp = Blueprint('skill', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@skill_bp.route('/add-skill', methods=['POST'])
def add_skill():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    form = AddSkillForm()

    # Dynamically load skill names from DB
    skill_names = db.session.execute(
        db.select(SkillName).order_by(SkillName.name)
        ).scalars().all()
    form.name.choices = [(sn.id, sn.name) for sn in skill_names]

    # Dynamically load categories from DB
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)
        ).scalars().all()
    form.category.choices = [(cat.id, cat.name) for cat in categories]

    if form.validate_on_submit():
        skill_name_id = form.name.data
        description = form.description.data
        category_id = form.category.data

        print(form.errors)
        print(f"Adding skill: {skill_name_id}, {description}, {category_id}")
        
        # Check if user already has this skill
        existing_skill = db.session.execute(
            db.select(Skill).filter_by(user_id=user.id, skill_name_id=skill_name_id)
        ).scalar_one_or_none()
        
        if existing_skill:
            skill_name = db.session.execute(
                db.select(SkillName).filter_by(id=skill_name_id)
            ).scalar_one_or_none()
            skill_name_text = skill_name.name if skill_name else "this skill"
            flash(f"You already have '{skill_name_text}'! If you want to update the description, please edit the existing skill from your skills list.", "warning")
            return redirect(url_for('dashboard.dashboard'))
        
        try:
            skill = Skill(skill_name_id=skill_name_id, description=description, category_id=category_id,
                            user_id=user.id)
            db.session.add(skill)
            db.session.commit()
            flash("Skill added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            flash(f"Skill was not created! {e}", "error")
            return redirect(url_for('dashboard.dashboard'))
    else:
        flash("Invalid form submission", "warning")

    return redirect(url_for('dashboard.dashboard'))
