from flask import Flask
from flask_socketio import SocketIO
from models import db
from routes import register_routes
from sockets import socketio

# 🎓 University Life Categories
category_data = [
    "Academic Tutoring",
    "Tech & Programming",
    "Campus Gigs & Freelance",
    "Creative Skills",
    "Career Prep & Productivity",
    "Languages & Culture",
    "Health & Wellness",
    "Music & Performing Arts",
    "Student Leadership & Advocacy",
    "Life Skills"
]

# 🧠 Realistic Student Skills
skill_name_data = [
    # Academic Tutoring
    "Calculus Help", "Intro to Python", "Organic Chemistry Tutoring", "Essay Editing", "Research Help",

    # Tech & Programming
    "Web Design", "Java Debugging", "SQL Queries", "App Prototyping", "GitHub Basics",

    # Campus Gigs & Freelance
    "Photography for Events", "Resume Headshots", "Dorm Moving Help", "Flyer Design", "Social Media Posts",

    # Creative Skills
    "Canva Design", "Spoken Word Coaching", "Podcast Editing", "Poster Art", "T-shirt Design",

    # Career Prep & Productivity
    "Resume Reviews", "LinkedIn Optimization", "Time Blocking", "Notion Templates", "Study Scheduling",

    # Languages & Culture
    "Beginner Spanish", "French Conversation Practice", "ASL Basics", "Cultural Exchange Partner",

    # Health & Wellness
    "Gym Partnering", "Meal Prepping on a Budget", "Mindfulness Techniques", "Yoga for Beginners",

    # Music & Performing Arts
    "Guitar Chords", "Music Production with FL Studio", "Dance Choreography", "Open Mic Performance Tips",

    # Student Leadership & Advocacy
    "Event Planning Tips", "Student Org Management", "Campus Fundraising", "Public Speaking Coaching",

    # Life Skills
    "Laundry Tips", "Cooking Nigerian Jollof", "Budgeting with Excel", "Roommate Conflict Resolution"
]


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)

    # Import all models to ensure they are registered with SQLAlchemy
    from models import User, Skill, SkillName, Category, Swap, SwapRequest, DiscussRequest, SwapMessage, SwapConversation

    with app.app_context():
        db.create_all() 

        print("Seeding Categories...")
        for cat in category_data:
            # Use SQLAlchemy 2.0 syntax
            stmt = db.select(Category).where(Category.name == cat)
            exists = db.session.execute(stmt).scalar_one_or_none()
            if not exists:
                new_category = Category(name=cat)
                db.session.add(new_category)
                print(f"  ✓ Added category: {cat}")

        print("Seeding Skill Names...")
        for skill in skill_name_data:
            # Use SQLAlchemy 2.0 syntax
            stmt = db.select(SkillName).where(SkillName.name == skill)
            exists = db.session.execute(stmt).scalar_one_or_none()
            if not exists:
                new_skill = SkillName(name=skill)
                db.session.add(new_skill)
                print(f"  ✓ Added skill: {skill}")

        try:
            db.session.commit()
            print("🎓 All set! Your campus swap board just got way more relevant")
        except Exception as e:
            db.session.rollback()
            print(f"Error during seeding: {e}")
            import traceback
            traceback.print_exc()

    # Register blueprints
    register_routes(app)

    # Initialize SocketIO with the app
    socketio.init_app(app, cors_allowed_origins="*")  # add CORS if needed

    return app

if __name__ == '__main__':
    app = create_app()

    socketio.run(app, debug=True, port=8000)
