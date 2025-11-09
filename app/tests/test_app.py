import pytest
import json
from app import app, workouts  # Import workouts dictionary

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True

    # Clear workouts before each test
    for category in workouts:
        workouts[category].clear()

    with app.test_client() as client:
        yield client

    # Clean up after test
    for category in workouts:
        workouts[category].clear()

def test_home_page(client):
    """Test home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'ACEest Fitness' in response.data

def test_get_categorized_workouts(client):
    """Test that workouts are returned with categories"""
    response = client.get('/api/workouts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'workouts' in data
    assert 'Warm-up' in data['workouts']
    assert 'Workout' in data['workouts']
    assert 'Cool-down' in data['workouts']

def test_add_workout_to_category(client):
    """Test adding workout to specific category"""
    workout_data = {
        'category': 'Warm-up',
        'exercise': 'Jumping Jacks',
        'duration': 10
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'Jumping Jacks' in data['message']

def test_add_workout_invalid_category(client):
    """Test adding workout with invalid category"""
    workout_data = {
        'category': 'InvalidCategory',
        'exercise': 'Running',
        'duration': 20
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Invalid category' in data['message']

def test_total_time_calculation(client):
    """Test that total time is calculated correctly"""
    # Verify starting with clean state
    response = client.get('/api/workouts')
    initial_data = json.loads(response.data)
    assert initial_data['total_time'] == 0, f"Expected 0, got {initial_data['total_time']}"

    # Add multiple workouts
    test_workouts = [
        {'category': 'Warm-up', 'exercise': 'Stretching', 'duration': 10},
        {'category': 'Workout', 'exercise': 'Push-ups', 'duration': 20},
        {'category': 'Cool-down', 'exercise': 'Walking', 'duration': 15}
    ]

    for workout in test_workouts:
        response = client.post('/api/workouts',
                               data=json.dumps(workout),
                               content_type='application/json')
        assert response.status_code == 200

    # Verify total time
    response = client.get('/api/workouts')
    data = json.loads(response.data)
    assert data['total_time'] == 45, f"Expected 45, got {data['total_time']}"
