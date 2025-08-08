import pytest
from app.models import User, Skill, Swap, db

class TestDashboardRoutes:
    """Test dashboard routes functionality."""
    
    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires login."""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data
    
    def test_dashboard_loads_when_logged_in(self, client, test_user):
        """Test that dashboard loads when user is logged in."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Welcome' in response.data
    
    def test_dashboard_shows_user_skills(self, client, test_user, test_skill):
        """Test that dashboard shows user's skills."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        # Should show the test skill
        assert b'Test Skill' in response.data
    
    def test_dashboard_shows_user_swaps(self, client, test_user, test_skill):
        """Test that dashboard shows user's swaps."""
        with client.application.app_context():
            # Create a swap for the test user
            swap = Swap(
                user_id=test_user.id,
                skill_id=test_skill.id,
                title="Test Swap",
                description="Test swap description",
                status="Open"
            )
            db.session.add(swap)
            db.session.commit()
        
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        # Should show the test swap
        assert b'Test Swap' in response.data
    
    def test_dashboard_shows_other_users_swaps(self, client, test_user, test_user2, test_skill):
        """Test that dashboard shows other users' swaps."""
        with client.application.app_context():
            # Create a swap for the second test user
            swap = Swap(
                user_id=test_user2.id,
                skill_id=test_skill.id,
                title="Other User's Swap",
                description="Another user's swap description",
                status="Open"
            )
            db.session.add(swap)
            db.session.commit()
        
        # Login as first user
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        # Should show the other user's swap
        assert b"Other User's Swap" in response.data
