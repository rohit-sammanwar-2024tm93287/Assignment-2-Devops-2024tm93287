import pytest
from app import app as flask_app, user_info, workouts_by_date

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test"""
    flask_app.config['TESTING'] = True

    # Clear all global state
    user_info.clear()
    workouts_by_date.clear()

    yield flask_app

    # Cleanup after test
    user_info.clear()
    workouts_by_date.clear()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def sample_user():
    """Return sample user data"""
    return {
        'name': 'Test User',
        'regn_id': '2024TM99999',
        'age': 28,
        'gender': 'M',
        'height': 175,
        'weight': 70
    }

@pytest.fixture(scope='function')
def sample_workout():
    """Return sample workout data"""
    return {
        'category': 'Workout',
        'exercise': 'Test Exercise',
        'duration': 30
    }

@pytest.fixture(scope='function')
def authenticated_client(client, sample_user):
    """Return a client with user already saved"""
    client.post('/api/user-info',
                json=sample_user)
    return client
