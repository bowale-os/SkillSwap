import pytest
from app.forms.signup import SignupForm
from app.forms.login import LoginForm
from app.forms.add_skill import AddSkillForm
from app.forms.make_swap import MakeSwapForm

class TestSignupForm:
    """Test SignupForm validation."""
    
    def test_valid_signup_form(self, app):
        """Test valid signup form data."""
        with app.app_context():
            form = SignupForm(data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            assert form.validate() is True
    
    def test_invalid_email(self, app):
        """Test signup form with invalid email."""
        with app.app_context():
            form = SignupForm(data={
                'name': 'John Doe',
                'email': 'invalid-email',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            assert form.validate() is False
            assert 'Invalid email address' in str(form.email.errors)
    
    def test_password_too_short(self, app):
        """Test signup form with password too short."""
        with app.app_context():
            form = SignupForm(data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': '123',
                'confirm_password': '123'
            })
            assert form.validate() is False
            assert 'Field must be between 6 and 255 characters long' in str(form.password.errors)
    
    def test_password_mismatch(self, app):
        """Test signup form with mismatched passwords."""
        with app.app_context():
            form = SignupForm(data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'password123',
                'confirm_password': 'differentpassword'
            })
            assert form.validate() is False
            assert 'Passwords must match' in str(form.confirm_password.errors)
    
    def test_name_too_short(self, app):
        """Test signup form with name too short."""
        with app.app_context():
            form = SignupForm(data={
                'name': 'J',
                'email': 'john@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            assert form.validate() is False
            assert 'Field must be between 2 and 100 characters long' in str(form.name.errors)

class TestLoginForm:
    """Test LoginForm validation."""
    
    def test_valid_login_form(self, app):
        """Test valid login form data."""
        with app.app_context():
            form = LoginForm(data={
                'email': 'john@example.com',
                'password': 'password123'
            })
            assert form.validate() is True
    
    def test_invalid_email(self, app):
        """Test login form with invalid email."""
        with app.app_context():
            form = LoginForm(data={
                'email': 'invalid-email',
                'password': 'password123'
            })
            assert form.validate() is False
            assert 'Invalid email address' in str(form.email.errors)
    
    def test_missing_password(self, app):
        """Test login form with missing password."""
        with app.app_context():
            form = LoginForm(data={
                'email': 'john@example.com',
                'password': ''
            })
            assert form.validate() is False
            assert 'This field is required' in str(form.password.errors)

class TestAddSkillForm:
    """Test AddSkillForm validation."""
    
    def test_valid_add_skill_form(self, app):
        """Test valid add skill form data."""
        with app.app_context():
            form = AddSkillForm(data={
                'name': 'Python Programming',
                'category': 'Tech & Programming',
                'description': 'I can help with Python programming and web development'
            })
            assert form.validate() is True
    
    def test_missing_skill_name(self, app):
        """Test add skill form with missing skill name."""
        with app.app_context():
            form = AddSkillForm(data={
                'name': '',
                'category': 'Tech & Programming',
                'description': 'I can help with Python programming'
            })
            assert form.validate() is False
            assert 'This field is required' in str(form.name.errors)
    
    def test_missing_description(self, app):
        """Test add skill form with missing description."""
        with app.app_context():
            form = AddSkillForm(data={
                'name': 'Python Programming',
                'category': 'Tech & Programming',
                'description': ''
            })
            assert form.validate() is False
            assert 'This field is required' in str(form.description.errors)
    
    def test_description_too_short(self, app):
        """Test add skill form with description too short."""
        with app.app_context():
            form = AddSkillForm(data={
                'name': 'Python Programming',
                'category': 'Tech & Programming',
                'description': 'Too short'
            })
            assert form.validate() is False
            assert 'Field must be between 20 and 500 characters long' in str(form.description.errors)

class TestMakeSwapForm:
    """Test MakeSwapForm validation."""
    
    def test_valid_make_swap_form(self, app):
        """Test valid make swap form data."""
        with app.app_context():
            form = MakeSwapForm(data={
                'desired_skill_name': 'Web Design',
                'offered_skill_id': '1',
                'description': 'I\'ll teach you Python in exchange for design help'
            })
            assert form.validate() is True
    
    def test_missing_desired_skill(self, app):
        """Test make swap form with missing desired skill."""
        with app.app_context():
            form = MakeSwapForm(data={
                'desired_skill_name': '',
                'offered_skill_id': '1',
                'description': 'I\'ll teach you Python in exchange for design help'
            })
            assert form.validate() is False
            assert 'This field is required' in str(form.desired_skill_name.errors)
    
    def test_missing_offered_skill(self, app):
        """Test make swap form with missing offered skill."""
        with app.app_context():
            form = MakeSwapForm(data={
                'desired_skill_name': 'Web Design',
                'offered_skill_id': '',
                'description': 'I\'ll teach you Python in exchange for design help'
            })
            assert form.validate() is False
            assert 'This field is required' in str(form.offered_skill_id.errors)
