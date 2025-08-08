# Testing Guide for SkillSwap

This directory contains comprehensive tests for the SkillSwap application using pytest.

## 🧪 What We Test

### 1. **Models** (`test_models.py`)
- User creation and validation
- Category and SkillName uniqueness
- Skill relationships and creation
- Swap functionality
- Database relationships and constraints

### 2. **Authentication** (`test_auth_routes.py`)
- User registration (signup)
- User login/logout
- Form validation
- Error handling for invalid credentials
- Session management

### 3. **Forms** (`test_forms.py`)
- SignupForm validation
- LoginForm validation
- AddSkillForm validation
- MakeSwapForm validation
- Field requirements and constraints

### 4. **Dashboard Routes** (`test_dashboard_routes.py`)
- Dashboard access control
- User-specific content display
- Skill and swap listings
- Authentication requirements

### 5. **Skill Routes** (`test_skill_routes.py`)
- Adding skills
- Viewing skills
- Deleting skills
- Authorization (users can only delete their own skills)

### 6. **Integration Tests** (`test_integration.py`)
- Complete user workflows
- End-to-end scenarios
- Error handling
- Cross-feature interactions

## 🚀 Running Tests

### Prerequisites
Make sure you have the testing dependencies installed:
```bash
pip install -r requirements.txt
```

### Basic Test Commands

1. **Run all tests:**
   ```bash
   pytest
   ```

2. **Run tests with verbose output:**
   ```bash
   pytest -v
   ```

3. **Run tests with coverage report:**
   ```bash
   pytest --cov=app --cov-report=html
   ```

4. **Run specific test file:**
   ```bash
   pytest tests/test_models.py
   ```

5. **Run specific test class:**
   ```bash
   pytest tests/test_models.py::TestUser
   ```

6. **Run specific test method:**
   ```bash
   pytest tests/test_models.py::TestUser::test_user_creation
   ```

### Test Categories

- **Unit Tests:** Test individual components in isolation
- **Integration Tests:** Test how components work together
- **End-to-End Tests:** Test complete user workflows

## 📊 Test Coverage

The tests are designed to cover:
- ✅ Database models and relationships
- ✅ Authentication and authorization
- ✅ Form validation
- ✅ Route functionality
- ✅ Error handling
- ✅ User workflows
- ✅ Data integrity

## 🔧 Test Configuration

### Fixtures (`conftest.py`)
The test suite uses pytest fixtures to provide:
- **`app`**: Flask application instance with test configuration
- **`client`**: Test client for making HTTP requests
- **`test_user`**: Pre-created test user
- **`test_user2`**: Second test user
- **`test_category`**: Test category
- **`test_skill_name`**: Test skill name
- **`test_skill`**: Test skill

### Test Database
- Uses SQLite in-memory database for fast, isolated tests
- Each test gets a fresh database
- No test data persists between tests

## 🎯 Test Examples

### Model Testing
```python
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
```

### Route Testing
```python
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
```

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors:**
   - Make sure you're running tests from the project root
   - Check that all dependencies are installed

2. **Database Errors:**
   - Tests use in-memory SQLite, so no external database needed
   - Each test gets a fresh database

3. **Authentication Issues:**
   - Use the provided fixtures for test users
   - Login before testing protected routes

### Debug Mode
Run tests with more verbose output:
```bash
pytest -v -s --tb=long
```

## 📈 Adding New Tests

### Guidelines for New Tests

1. **Test Structure:**
   - Use descriptive test names
   - Group related tests in classes
   - Use fixtures for common setup

2. **Test Data:**
   - Use fixtures for test data
   - Don't rely on external data
   - Clean up after tests

3. **Assertions:**
   - Test both positive and negative cases
   - Check database state when relevant
   - Verify HTTP status codes and responses

### Example Test Template
```python
def test_new_feature(self, client, app):
    """Test description of what this test does."""
    # Setup
    with app.app_context():
        # Test data setup
        
    # Action
    response = client.post('/new-route', data={
        'field': 'value'
    }, follow_redirects=True)
    
    # Assertions
    assert response.status_code == 200
    assert b'Expected content' in response.data
    
    # Database assertions
    with app.app_context():
        # Check database state
        pass
```

## 🎉 Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- Fast execution (under 30 seconds)
- No external dependencies
- Clear pass/fail results
- Coverage reporting

Run tests before committing to ensure code quality!
