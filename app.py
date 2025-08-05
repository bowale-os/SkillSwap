from flask import Flask, jsonify, render_template, url_for, session, redirect, flash, request
from sqlalchemy import exists, select
from forms import SignupForm, LoginForm, AddSkillForm, MakeSwapForm
from models import db, User, Skill, Swap, SkillName, Category, SwapConversation, SwapMessage, SwapRequest
from flask_migrate import Migrate
from dotenv import load_dotenv
load_dotenv()

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        user = User(name=name, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            flash(f"Account could not be created, {e} error")
            return render_template('signup.html', form=form)
        
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Query user by email
        try:
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

            if user and password == user.password:
                session['user_id'] = user.id  
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))  
            else:
                flash("Invalid email or password", "danger")
        except Exception as e:
            flash(f"Contact admin. {e} error")

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    
    #stuff for skill and swap forms
    form = AddSkillForm()
    swap_form = MakeSwapForm()

    skill_names = db.session.execute(
        db.select(SkillName)
    ).scalars().all()

    categories = db.session.execute(
        db.select(Category)
    ).scalars().all()

    form.name.choices = [(skill_name.id, skill_name.name) for skill_name in skill_names]
    form.category.choices = [(category.id, category.name) for category in categories]

    #stuff for skill display

    user_skills = db.session.execute(
            db.select(Skill).filter_by(user_id=user_id)
    ).scalars().all()

    other_skill_names = db.session.execute(
        db.select(SkillName)
    ).scalars().all()

     # 👇 Dynamically set SelectField choices for the swap form
    swap_form.desired_skill_name.choices = [(skill_name.id, skill_name.name) for skill_name in other_skill_names]
    swap_form.offered_skill_id.choices = [(skill.id, skill.skill_name.name) for skill in user_skills]

    current_user = db.session.execute(
        db.select(User).filter_by(id=user_id)
    ).scalar_one_or_none()


    sent_swap_requests = db.session.execute(
        db.select(SwapRequest).filter_by(sender_id=user_id)
    ).scalars().all()

    received_swap_requests = db.session.execute(
        db.select(SwapRequest).filter_by(recipient_id=user_id)
    ).scalars().all()

    # Get the skill_name_ids of the user's skills to make displayed swaps correct
    user_skill_name_ids = [skill.skill_name_id for skill in user_skills if skill.skill_name_id]
    
    # Subquery: Check if a SwapRequest exists from the current user for this Swap
    subquery = (
        select(SwapRequest.id)
        .filter(
            SwapRequest.swap_id == Swap.id,
            SwapRequest.sender_id == user_id
        )
        .correlate(Swap)  # 👈 THIS is what tells SQLAlchemy to treat Swap.id as coming from the outer query
    )

    # Main query: Get swaps that the user hasn’t requested yet to display in swap stream
    unrequested_swaps = db.session.execute(
        select(Swap).filter(
            (Swap.user_id != user_id) &
            (Swap.is_satisfied == False) &
            (~exists(subquery))&
            (Swap.desired_skill_name_id.in_
             (user_skill_name_ids))
        )
    ).scalars().all()


    
    return render_template('dashboard.html',
                           form=form, 
                           swap_form=swap_form, 
                           current_user = current_user,
                           skills=user_skills,
                           swaps=unrequested_swaps,
                           sent_swap_requests = sent_swap_requests if sent_swap_requests else None,
                           received_swap_requests = received_swap_requests if received_swap_requests else None
                           )


@app.route('/add-skill', methods=['POST'])
def add_skill():
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))

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
        
        try:
            skill = Skill(skill_name_id=skill_name_id, description=description, category_id=category_id,
                          user_id=user_id)
            db.session.add(skill)
            db.session.commit()
            flash("Skill added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash(f"Skill was not created! {e}", "error")
            return redirect(url_for('dashboard'))
    else:
        flash("Invalid form submission", "warning")

    return redirect(url_for('dashboard'))


@app.route('/send_swap_request/<string:swap_id>', methods=['POST'])
def send_swap_request(swap_id):
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    sender_skill_id = request.form.get('sender_skill_id')
    
    swap = db.get_or_404(Swap, swap_id)
    recipient_id = swap.user_id
    recipient_skill_id = swap.offered_skill_id
    
    try:
        swap_request = SwapRequest(
        swap_id=swap_id,
        sender_id = user_id,
        sender_skill_id = sender_skill_id,
        recipient_id = recipient_id,
        recipient_skill_id = recipient_skill_id
        )

        db.session.add(swap_request)
        db.session.commit()
        flash("Swap request was made successfully!", "success")

    except Exception as e:
        print(f"Error: {e}")
        flash(f"Swap request was not created! {e}", "error")
        return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))




@app.route('/make-swap', methods=['POST'])
def make_swap():
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    
    form = MakeSwapForm()

    user_skills = db.session.execute(
        db.select(Skill).filter_by(user_id=user_id)
    ).scalars().all()

    other_skill_names = db.session.execute(
        db.select(SkillName)
    ).scalars().all()

     # 👇 Dynamically set SelectField choices for the swap form
    form.offered_skill_id.choices = [(skill.id, skill.skill_name.name) for skill in user_skills]
    form.desired_skill_name.choices = [(skill_name.id, skill_name.name) for skill_name in other_skill_names]

    if form.validate_on_submit():
        desired_skill_name =  form.desired_skill_name.data
        offered_skill_id = form.offered_skill_id.data
        description = form.description.data

        try:
            swap = Swap(desired_skill_name_id=desired_skill_name, offered_skill_id=offered_skill_id, description=description, user_id=user_id)
            db.session.add(swap)
            db.session.commit()
            flash("Your swap request has been added to the Swap-Stream!", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash(f"Some error occured wile creating your swap request. Please message admin. ", "error")
            return redirect(url_for('dashboard'))
        
        return redirect(url_for('dashboard'))


@app.route('/discuss_swap/<string:request_id>', methods=['GET'])
def discuss_swap_request(user_id):
    
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    pass
    
    
    # return render_template('discuss-swap.html')


@app.route('/delete_swap_request/<string:request_id>', methods=['GET'])
def delete_swap_request(request_id):
    
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    
    try:
        swap_request = db.get_or_404(SwapRequest, request_id)
        if swap_request:
            db.session.delete(swap_request)
            db.session.commit()
        else:
            flash("Swap Request was not found.")
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"encountered this error, {e}")
        flash("Please reach out to admin")
        return redirect(url_for('dashboard'))
    
    flash("Swap Request was removed successfully.")
    return redirect(url_for('dashboard'))

@app.route('/edit_skill_desc/<string:skill_id>', methods=['GET', 'POST'])
def edit_skill_desc(skill_id):
    
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    
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
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"encountered this error, {e}")
        flash("Please reach out to admin")
        return redirect(url_for('dashboard'))
    
    flash("Skill was edited successfully.")
    return redirect(url_for('dashboard'))

@app.route('/delete_skill/<string:skill_id>', methods=['GET'])
def delete_skill(skill_id):
    user_id = session.get('user_id', None)
    if not user_id:
        return redirect(url_for('login'))
    
    try:
        skill = db.get_or_404(Skill, skill_id)
        if skill.user_id != user_id:
            flash("You are not authorized to delete this skill!", "error")
            return redirect(url_for('dashboard'))
        
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
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=8888)