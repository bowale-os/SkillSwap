from flask import Blueprint, render_template, redirect, url_for, session
from app.forms.add_skill import AddSkillForm
from app.models import db, User, Skill, SkillName, Category

skill_bp = Blueprint('skill', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@skill_bp.route('/add_skill', methods=['GET', 'POST'])
def add_skill():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    form = AddSkillForm()
    form.name.choices = [(name.name, name.name) for name in SkillName.query.all()]
    form.category.choices = [(cat.name, cat.name) for cat in Category.query.all()]

    if form.validate_on_submit():
        skill_name = form.name.data
        category_name = form.category.data
        description = form.description.data

        skill_name_obj = SkillName.query.filter_by(name=skill_name).first()
        category_obj = Category.query.filter_by(name=category_name).first()

        new_skill = Skill(
            user_id=user.id,
            name_id=skill_name_obj.id,
            category_id=category_obj.id,
            description=description
        )
        db.session.add(new_skill)
        db.session.commit()

        return redirect(url_for('dashboard.dashboard'))

    return render_template('add_skill.html', form=form)
