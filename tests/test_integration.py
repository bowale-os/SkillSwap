import pytest
from app.models import User, Skill, Swap, SwapRequest, db
from werkzeug.security import generate_password_hash

class TestIntegrationWorkflow:
    """Test complete user workflows."""
    
    def test_complete_user_journey(self, client, app):
        """Test a complete user journey: signup, add skill, create swap, make request."""
        with app.app_context():
            # 1. User signs up
            response = client.post('/signup', data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check user was created
            user = db.session.execute(
                db.select(User).filter_by(email='john@example.com')
            ).scalar_one_or_none()
            assert user is not None
            
            # 2. User adds a skill
            response = client.post('/add-skill', data={
                'skill_name': 'Python Programming',
                'description': 'I can help with Python programming',
                'proficiency_level': 'Intermediate'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check skill was created
            skill = db.session.execute(
                db.select(Skill).filter_by(user_id=user.id)
            ).scalar_one_or_none()
            assert skill is not None
            assert skill.description == 'I can help with Python programming'
            
            # 3. User creates a swap
            response = client.post('/make-swap', data={
                'title': 'Python for Design',
                'description': 'I\'ll teach you Python in exchange for design help',
                'skill_id': str(skill.id)
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check swap was created
            swap = db.session.execute(
                db.select(Swap).filter_by(user_id=user.id)
            ).scalar_one_or_none()
            assert swap is not None
            assert swap.title == 'Python for Design'
    
    def test_swap_request_workflow(self, client, app, test_user, test_user2, test_skill):
        """Test the complete swap request workflow."""
        with app.app_context():
            # Create a swap for the first user
            swap = Swap(
                user_id=test_user.id,
                skill_id=test_skill.id,
                title="Python for Design",
                description="I'll teach you Python in exchange for design help",
                status="Open"
            )
            db.session.add(swap)
            db.session.commit()
            
            # Second user logs in
            client.post('/login', data={
                'email': 'test2@example.com',
                'password': 'password123'
            })
            
            # Second user requests the swap
            response = client.post(f'/request-swap/{swap.id}', data={
                'message': 'I would like to learn Python!'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check swap request was created
            swap_request = db.session.execute(
                db.select(SwapRequest).filter_by(
                    sender_id=test_user2.id,
                    recipient_id=test_user.id,
                    swap_id=swap.id
                )
            ).scalar_one_or_none()
            assert swap_request is not None
            assert swap_request.message == 'I would like to learn Python!'
    
    def test_user_profile_workflow(self, client, app, test_user):
        """Test user profile and skill management workflow."""
        with app.app_context():
            # User logs in
            client.post('/login', data={
                'email': 'test@example.com',
                'password': 'password123'
            })
            
            # User views their profile/dashboard
            response = client.get('/dashboard')
            assert response.status_code == 200
            assert b'Test User' in response.data
            
            # User adds multiple skills
            skills_data = [
                {
                    'skill_name': 'Python Programming',
                    'description': 'I can help with Python programming',
                    'proficiency_level': 'Intermediate'
                },
                {
                    'skill_name': 'Web Design',
                    'description': 'I can help with web design',
                    'proficiency_level': 'Beginner'
                }
            ]
            
            for skill_data in skills_data:
                response = client.post('/add-skill', data=skill_data, follow_redirects=True)
                assert response.status_code == 200
            
            # Check all skills were created
            skills = db.session.execute(
                db.select(Skill).filter_by(user_id=test_user.id)
            ).scalars().all()
            assert len(skills) >= 3  # Including the test_skill from fixture
            
            # User views their skills
            response = client.get('/skills')
            assert response.status_code == 200
            assert b'Python Programming' in response.data
            assert b'Web Design' in response.data
    
    def test_error_handling(self, client, app):
        """Test error handling in the application."""
        # Test accessing non-existent route
        response = client.get('/non-existent-route')
        assert response.status_code == 404
        
        # Test accessing protected route without login
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data
        
        # Test invalid form submission
        response = client.post('/signup', data={
            'name': '',
            'email': 'invalid-email',
            'password': '123',
            'confirm_password': 'different'
        })
        assert response.status_code == 200
        # Should show validation errors
        assert b'This field is required' in response.data or b'Invalid email address' in response.data
