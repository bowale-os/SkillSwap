from flask import Flask
from flask_socketio import SocketIO
from models import db, Category, SkillName
from routes import register_routes
from sockets import socketio

# 🎓 University Life Categories (expanded)
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
    "Life Skills",
    "Financial Literacy",
    "Mental Health & Self-Care",
    "Outdoor & Adventure",
    "Entrepreneurship & Startups",
]

# 🧠 Realistic Student Skills (expanded)
skill_name_data = [
    # Academic Tutoring
    "Calculus Help", "Intro to Python", "Organic Chemistry Tutoring", "Essay Editing", "Research Help",
    "Statistics Fundamentals", "Physics Problem Solving", "Linear Algebra Assistance", "Essay Writing Tips",

    # Tech & Programming
    "Web Design", "Java Debugging", "SQL Queries", "App Prototyping", "GitHub Basics",
    "Data Visualization with Python", "Intro to Machine Learning", "Linux Command Line", "APIs with Flask",

    # Campus Gigs & Freelance
    "Photography for Events", "Resume Headshots", "Dorm Moving Help", "Flyer Design", "Social Media Posts",
    "Tutoring Scheduling Assistant", "Event Setup Crew", "Campus Tour Guide", "Freelance Writing",

    # Creative Skills
    "Canva Design", "Spoken Word Coaching", "Podcast Editing", "Poster Art", "T-shirt Design",
    "Creative Writing Workshops", "Digital Illustration Basics", "Video Editing Basics", "Photography Editing",

    # Career Prep & Productivity
    "Resume Reviews", "LinkedIn Optimization", "Time Blocking", "Notion Templates", "Study Scheduling",
    "Interview Practice", "Networking Strategies", "Public Speaking Confidence", "Project Management Basics",

    # Languages & Culture
    "Beginner Spanish", "French Conversation Practice", "ASL Basics", "Cultural Exchange Partner",
    "Japanese for Beginners", "Meditation & Mindfulness in Different Cultures", "German Basics", "Chinese Mandarin Intro",

    # Health & Wellness
    "Gym Partnering", "Meal Prepping on a Budget", "Mindfulness Techniques", "Yoga for Beginners",
    "Stress Management", "Sleep Hygiene Tips", "Healthy Cooking", "Running Form Coaching",

    # Music & Performing Arts
    "Guitar Chords", "Music Production with FL Studio", "Dance Choreography", "Open Mic Performance Tips",
    "Beatboxing Basics", "Stage Presence Coaching", "Piano Basics", "Songwriting Techniques",

    # Student Leadership & Advocacy
    "Event Planning Tips", "Student Org Management", "Campus Fundraising", "Public Speaking Coaching",
    "Conflict Resolution in Groups", "Volunteer Coordination", "Leadership Skills", "Advocacy Strategies",

    # Life Skills
    "Laundry Tips", "Cooking Nigerian Jollof", "Budgeting with Excel", "Roommate Conflict Resolution",
    "Basic Car Maintenance", "Travel Planning on a Budget", "Time Management", "Personal Safety",

    # Financial Literacy
    "Credit Score Basics", "Student Loan Management", "Investment 101", "Tax Filing for Beginners", "Building an Emergency Fund",

    # Mental Health & Self-Care
    "Dealing with Anxiety", "Building Healthy Habits", "Meditation for Beginners", "Journaling for Mental Clarity",

    # Outdoor & Adventure
    "Backpacking Essentials", "Rock Climbing Basics", "Camping Cooking Tips", "Hiking Trail Recommendations",

    # Entrepreneurship & Startups
    "Pitch Deck Creation", "Lean Startup Methodology", "Building an MVP", "Finding Co-Founders", "Marketing on a Budget",
]


def create_app():
    print("Starting create_app() - seeding will run if needed...")
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        db.create_all()

        print("Seeding Categories...")
        for cat in category_data:
            stmt = db.select(Category).where(Category.name == cat)
            exists = db.session.execute(stmt).scalar_one_or_none()
            if not exists:
                new_category = Category(name=cat)
                db.session.add(new_category)
                print(f" Added category: {cat}")

        print("Seeding Skill Names...")
        for skill in skill_name_data:
            stmt = db.select(SkillName).where(SkillName.name == skill)
            exists = db.session.execute(stmt).scalar_one_or_none()
            if not exists:
                new_skill = SkillName(name=skill)
                db.session.add(new_skill)
                print(f"  Added skill: {skill}")

        try:
            db.session.commit()
            print("All set! Your campus swap board just got way more relevant")
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
