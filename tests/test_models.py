import pytest
from app.models import User, Category, SkillName, Skill, Swap, SwapRequest, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class TestUser:
    """Test User model functionality."""
    
    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                name="John Doe",
                email="john@example.com",
                password=generate_password_hash("password123")
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.name == "John Doe"
            assert user.email == "john@example.com"
            assert check_password_hash(user.password, "password123")
            assert isinstance(user.created_at, datetime)
    
    def test_user_email_uniqueness(self, app, test_user):
        """Test that email addresses must be unique."""
        with app.app_context():
            duplicate_user = User(
                name="Another User",
                email="test@example.com",  # Same email as test_user
                password=generate_password_hash("password123")
            )
            db.session.add(duplicate_user)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()
    
    def test_user_relationships(self, app, test_user, test_skill):
        """Test user relationships with skills."""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            assert len(user.skills) == 1
            assert user.skills[0].id == test_skill.id

class TestCategory:
    """Test Category model functionality."""
    
    def test_category_creation(self, app):
        """Test creating a new category."""
        with app.app_context():
            category = Category(name="Programming")
            db.session.add(category)
            db.session.commit()
            
            assert category.id is not None
            assert category.name == "Programming"
    
    def test_category_name_uniqueness(self, app, test_category):
        """Test that category names must be unique."""
        with app.app_context():
            duplicate_category = Category(name="Test Category")  # Same name as test_category
            db.session.add(duplicate_category)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()

class TestSkillName:
    """Test SkillName model functionality."""
    
    def test_skill_name_creation(self, app):
        """Test creating a new skill name."""
        with app.app_context():
            skill_name = SkillName(name="Python Programming")
            db.session.add(skill_name)
            db.session.commit()
            
            assert skill_name.id is not None
            assert skill_name.name == "Python Programming"
    
    def test_skill_name_uniqueness(self, app, test_skill_name):
        """Test that skill names must be unique."""
        with app.app_context():
            duplicate_skill_name = SkillName(name="Test Skill")  # Same name as test_skill_name
            db.session.add(duplicate_skill_name)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()

class TestSkill:
    """Test Skill model functionality."""
    
    def test_skill_creation(self, app, test_user, test_skill_name):
        """Test creating a new skill."""
        with app.app_context():
            skill = Skill(
                user_id=test_user.id,
                skill_name_id=test_skill_name.id,
                description="I can help with Python programming",
                proficiency_level="Intermediate"
            )
            db.session.add(skill)
            db.session.commit()
            
            assert skill.id is not None
            assert skill.user_id == test_user.id
            assert skill.skill_name_id == test_skill_name.id
            assert skill.description == "I can help with Python programming"
            assert skill.proficiency_level == "Intermediate"
    
    def test_skill_relationships(self, app, test_skill):
        """Test skill relationships with user and skill_name."""
        with app.app_context():
            skill = db.session.get(Skill, test_skill.id)
            assert skill.user.name == "Test User"
            assert skill.skill_name.name == "Test Skill"

class TestSwap:
    """Test Swap model functionality."""
    
    def test_swap_creation(self, app, test_user, test_skill):
        """Test creating a new swap."""
        with app.app_context():
            swap = Swap(
                user_id=test_user.id,
                skill_id=test_skill.id,
                title="Python for Design",
                description="I'll teach you Python in exchange for design help",
                status="Open"
            )
            db.session.add(swap)
            db.session.commit()
            
            assert swap.id is not None
            assert swap.user_id == test_user.id
            assert swap.skill_id == test_skill.id
            assert swap.title == "Python for Design"
            assert swap.status == "Open"
    
    def test_swap_relationships(self, app, test_user, test_skill):
        """Test swap relationships."""
        with app.app_context():
            swap = Swap(
                user_id=test_user.id,
                skill_id=test_skill.id,
                title="Test Swap",
                description="Test description",
                status="Open"
            )
            db.session.add(swap)
            db.session.commit()
            
            # Test relationship with user
            user = db.session.get(User, test_user.id)
            assert len(user.swaps) == 1
            assert user.swaps[0].id == swap.id
