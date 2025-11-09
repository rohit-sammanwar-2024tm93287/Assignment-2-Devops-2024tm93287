import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'ACEest Fitness' in response.data

def test_get_workout_chart(client):
    """Test workout chart endpoint"""
    response = client.get('/api/workout-chart')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Warm-up' in data
    assert 'Workout' in data
    assert 'Cool-down' in data
    assert isinstance(data['Warm-up'], list)

def test_get_diet_chart(client):
    """Test diet chart endpoint"""
    response = client.get('/api/diet-chart')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Weight Loss' in data
    assert 'Muscle Gain' in data
    assert 'Endurance' in data
    assert 'breakfast' in data['Weight Loss']

def test_add_workout(client):
    """Test adding a workout"""
    workout_data = {
        'category': 'Workout',
        'exercise': 'Squats',
        'duration': 25
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

def test_workout_chart_has_exercises(client):
    """Test that workout chart contains expected exercises"""
    response = client.get('/api/workout-chart')
    data = json.loads(response.data)
    assert 'Push-ups' in data['Workout']
    assert 'Squats' in data['Workout']
    assert 'Jumping Jacks' in data['Warm-up']

def test_diet_chart_structure(client):
    """Test diet chart has proper structure"""
    response = client.get('/api/diet-chart')
    data = json.loads(response.data)

    for goal in ['Weight Loss', 'Muscle Gain', 'Endurance']:
        assert goal in data
        assert 'breakfast' in data[goal]
        assert 'lunch' in data[goal]
        assert 'dinner' in data[goal]
        assert 'snacks' in data[goal]
