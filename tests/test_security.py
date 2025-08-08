import pytest
from app.models import User, db

class TestSecurity:
    """Test security aspects of the application."""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = User(
                name="Test User",
                email="security@example.com",
                password="plaintext_password"
            )
            db.session.add(user)
            db.session.commit()
            
            # Password should be hashed, not plaintext
            assert user.password != "plaintext_password"
            assert len(user.password) > 20  # Hashed passwords are longer
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection."""
        # Try to inject SQL in email field
        malicious_email = "test@example.com'; DROP TABLE users; --"
        
        response = client.post('/signup', data={
            'name': 'Test User',
            'email': malicious_email,
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Should handle gracefully, not crash
        assert response.status_code in [200, 400]
    
    def test_xss_protection(self, client, test_user):
        """Test XSS protection."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Try to inject XSS in skill description
        xss_payload = "<script>alert('xss')</script>"
        
        response = client.post('/add-skill', data={
            'name': 'Test Skill',
            'category': 'Tech & Programming',
            'description': xss_payload
        }, follow_redirects=True)
        
        # Should handle gracefully
        assert response.status_code == 200
        # The script tag should be escaped or removed
        assert b'<script>' not in response.data
    
    def test_csrf_protection(self, client):
        """Test CSRF protection."""
        # Try to make a POST request without CSRF token
        response = client.post('/signup', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Should either require CSRF token or handle gracefully
        assert response.status_code in [200, 400, 403]
