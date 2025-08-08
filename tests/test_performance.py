import pytest
import time
from app.models import User, Skill, db

class TestPerformance:
    """Test application performance (basic examples)."""
    
    def test_dashboard_load_time(self, client, test_user):
        """Test dashboard loads within acceptable time."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        start_time = time.time()
        response = client.get('/dashboard')
        load_time = time.time() - start_time
        
        assert response.status_code == 200
        assert load_time < 2.0  # Should load within 2 seconds
    
    def test_database_query_performance(self, app, test_user):
        """Test database query performance."""
        with app.app_context():
            start_time = time.time()
            
            # Simulate a complex query
            skills = db.session.execute(
                db.select(Skill).filter_by(user_id=test_user.id)
            ).scalars().all()
            
            query_time = time.time() - start_time
            
            assert query_time < 0.1  # Should complete within 100ms
            assert len(skills) >= 0
