import pytest
from app import create_app
from app.models import db, User, Category, SkillName, Skill, Swap, SwapRequest
from werkzeug.security import generate_password_hash
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with testing configuration
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            name="Test User",
            email="test@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_user2(app):
    """Create a second test user."""
    with app.app_context():
        user = User(
            name="Test User 2",
            email="test2@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_category(app):
    """Create a test category."""
    with app.app_context():
        category = Category(name="Test Category")
        db.session.add(category)
        db.session.commit()
        return category

@pytest.fixture
def test_skill_name(app):
    """Create a test skill name."""
    with app.app_context():
        skill_name = SkillName(name="Test Skill")
        db.session.add(skill_name)
        db.session.commit()
        return skill_name

@pytest.fixture
def test_skill(app, test_user, test_skill_name):
    """Create a test skill."""
    with app.app_context():
        skill = Skill(
            user_id=test_user.id,
            skill_name_id=test_skill_name.id,
            description="Test skill description",
            proficiency_level="Beginner"
        )
        db.session.add(skill)
        db.session.commit()
        return skill
