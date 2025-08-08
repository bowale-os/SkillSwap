import pytest
from app.models import User, db
from werkzeug.security import generate_password_hash

class TestAuthRoutes:
    """Test authentication routes functionality."""
    
    def test_signup_page_loads(self, client):
        """Test that the signup page loads correctly."""
        response = client.get('/signup')
        assert response.status_code == 200
        assert b'Sign Up' in response.data
    
    def test_signup_success(self, client, app):
        """Test successful user registration."""
        with app.app_context():
            response = client.post('/signup', data={
                'name': 'New User',
                'email': 'newuser@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            # Check if user was created in database
            user = db.session.execute(
                db.select(User).filter_by(email='newuser@example.com')
            ).scalar_one_or_none()
            assert user is not None
            assert user.name == 'New User'
    
    def test_signup_duplicate_email(self, client, test_user):
        """Test signup with existing email."""
        response = client.post('/signup', data={
            'name': 'Another User',
            'email': 'test@example.com',  # Same email as test_user
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200  # Should stay on signup page
        assert b'Error creating account' in response.data
    
    def test_signup_password_mismatch(self, client):
        """Test signup with mismatched passwords."""
        response = client.post('/signup', data={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        })
        
        assert response.status_code == 200
        assert b'Passwords must match' in response.data
    
    def test_login_page_loads(self, client):
        """Test that the login page loads correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check if user is logged in by looking for dashboard content
        assert b'Dashboard' in response.data or b'Welcome' in response.data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_logout(self, client, test_user):
        """Test logout functionality."""
        # First login
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data
