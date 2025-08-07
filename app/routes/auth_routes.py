# routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models import db, User
from app.forms.signup import SignupForm
from app.forms.login import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            flash(f"Error creating account: {e}", "danger")
    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).filter_by(email=form.email.data)
        ).scalar_one_or_none()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash("Login successful", "success")
            return redirect(url_for('dashboard.dashboard'))
        flash("Invalid email or password", "danger")
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
