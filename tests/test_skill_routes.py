import pytest
from app.models import User, Skill, SkillName, db

class TestSkillRoutes:
    """Test skill routes functionality."""
    
    def test_add_skill_requires_login(self, client):
        """Test that adding a skill requires login."""
        response = client.get('/add-skill', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data
    
    def test_add_skill_page_loads_when_logged_in(self, client, test_user):
        """Test that add skill page loads when user is logged in."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/add-skill')
        assert response.status_code == 200
        assert b'Add Skill' in response.data
    
    def test_add_skill_success(self, client, test_user, test_skill_name):
        """Test successful skill addition."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.post('/add-skill', data={
            'skill_name': 'Test Skill',
            'description': 'I can help with this skill',
            'proficiency_level': 'Intermediate'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check if skill was created in database
        with client.application.app_context():
            skill = db.session.execute(
                db.select(Skill).filter_by(user_id=test_user.id)
            ).scalar_one_or_none()
            assert skill is not None
            assert skill.description == 'I can help with this skill'
            assert skill.proficiency_level == 'Intermediate'
    
    def test_add_skill_missing_data(self, client, test_user):
        """Test adding skill with missing data."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.post('/add-skill', data={
            'skill_name': '',
            'description': '',
            'proficiency_level': ''
        })
        
        assert response.status_code == 200
        # Should stay on add skill page with errors
        assert b'Add Skill' in response.data
    
    def test_view_skills_requires_login(self, client):
        """Test that viewing skills requires login."""
        response = client.get('/skills', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data
    
    def test_view_skills_when_logged_in(self, client, test_user, test_skill):
        """Test viewing skills when logged in."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/skills')
        assert response.status_code == 200
        # Should show the test skill
        assert b'Test Skill' in response.data
    
    def test_delete_skill_requires_login(self, client):
        """Test that deleting a skill requires login."""
        response = client.post('/delete-skill/1', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data
    
    def test_delete_skill_success(self, client, test_user, test_skill):
        """Test successful skill deletion."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.post(f'/delete-skill/{test_skill.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Check if skill was deleted from database
        with client.application.app_context():
            skill = db.session.get(Skill, test_skill.id)
            assert skill is None
    
    def test_delete_skill_not_owner(self, client, test_user, test_user2, test_skill):
        """Test deleting a skill that doesn't belong to the user."""
        # Login as second user
        client.post('/login', data={
            'email': 'test2@example.com',
            'password': 'password123'
        })
        
        response = client.post(f'/delete-skill/{test_skill.id}', follow_redirects=True)
        assert response.status_code == 200
        # Should not be able to delete another user's skill
        
        # Check if skill still exists in database
        with client.application.app_context():
            skill = db.session.get(Skill, test_skill.id)
            assert skill is not None
