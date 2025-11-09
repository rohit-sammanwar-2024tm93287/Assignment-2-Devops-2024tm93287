import pytest
import json
from app import app, user_info, workouts_by_date

@pytest.fixture(scope='function')
def client():
    """Create a test client with clean state"""
    app.config['TESTING'] = True

    # Clear state before each test
    user_info.clear()
    workouts_by_date.clear()

    with app.test_client() as test_client:
        yield test_client

    # Cleanup after test
    user_info.clear()
    workouts_by_date.clear()

def test_add_workout_without_user_info(client):
    """Test that workout without user info returns 400 error"""
    # Verify clean state
    assert len(user_info) == 0, "user_info should be empty"

    workout_data = {
        'category': 'Workout',
        'exercise': 'Push-ups',
        'duration': 20
    }

    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'user info' in data['message'].lower()

def test_export_pdf_without_user_info(client):
    """Test PDF export fails without user info"""
    # Verify clean state
    assert len(user_info) == 0, "user_info should be empty"

    response = client.get('/api/export-pdf')

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'user info' in data['message'].lower()

def test_add_workout_with_user_info(client):
    """Test adding workout WITH user info succeeds"""
    # First add user info
    user_data = {
        'name': 'Test User',
        'regn_id': 'TM001',
        'age': 28,
        'gender': 'M',
        'height': 180,
        'weight': 75
    }

    response = client.post('/api/user-info',
                           data=json.dumps(user_data),
                           content_type='application/json')

    assert response.status_code == 200, f"Failed to save user info: {response.data}"

    # Debug: Check if user_info was populated
    print(f"\nDEBUG: user_info after POST = {user_info}")

    # Verify user_info is populated
    assert len(user_info) > 0, f"user_info should be populated but got: {user_info}"
    assert 'weight' in user_info, f"weight key missing from user_info: {user_info.keys()}"
    assert user_info['weight'] == 75, f"Expected weight 75, got {user_info.get('weight')}"

    # Now add workout (should succeed)
    workout_data = {
        'category': 'Workout',
        'exercise': 'Push-ups',
        'duration': 20
    }

    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')

    assert response.status_code == 200, f"Failed to add workout: {response.data}"
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'calories' in data['workout']
    assert data['workout']['calories'] > 0

def test_save_user_info(client):
    """Test saving user information"""
    user_data = {
        'name': 'John Doe',
        'regn_id': '2024TM12345',
        'age': 25,
        'gender': 'M',
        'height': 175,
        'weight': 70
    }

    response = client.post('/api/user-info',
                           data=json.dumps(user_data),
                           content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'bmi' in data['user_info']
    assert 'bmr' in data['user_info']

    # Verify the global user_info was updated
    assert len(user_info) > 0
    assert user_info['name'] == 'John Doe'

def test_get_user_info(client):
    """Test retrieving user information"""
    # Initially empty
    response = client.get('/api/user-info')
    data = json.loads(response.data)
    assert data['user_info'] == {}

    # Add user info
    user_data = {
        'name': 'Jane Smith',
        'regn_id': '2024TM67890',
        'age': 30,
        'gender': 'F',
        'height': 165,
        'weight': 60
    }
    client.post('/api/user-info', data=json.dumps(user_data), content_type='application/json')

    # Retrieve it
    response = client.get('/api/user-info')
    data = json.loads(response.data)
    assert data['user_info']['name'] == 'Jane Smith'
    assert data['user_info']['weight'] == 60
