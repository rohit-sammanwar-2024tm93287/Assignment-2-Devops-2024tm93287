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

def test_workout_stats_endpoint(client):
    """Test workout statistics endpoint"""
    response = client.get('/api/workout-stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'categories' in data
    assert 'durations' in data
    assert len(data['categories']) == len(data['durations'])

def test_workout_stats_structure(client):
    """Test that stats have correct structure"""
    response = client.get('/api/workout-stats')
    data = json.loads(response.data)

    assert isinstance(data['categories'], list)
    assert isinstance(data['durations'], list)
    assert 'Warm-up' in data['categories']
    assert 'Workout' in data['categories']
    assert 'Cool-down' in data['categories']

def test_add_workout_updates_stats(client):
    """Test that adding workout updates statistics"""
    # Get initial stats
    response1 = client.get('/api/workout-stats')
    data1 = json.loads(response1.data)
    initial_total = sum(data1['durations'])

    # Add a workout
    workout_data = {
        'category': 'Workout',
        'exercise': 'Burpees',
        'duration': 30
    }
    client.post('/api/workouts',
                data=json.dumps(workout_data),
                content_type='application/json')

    # Get updated stats
    response2 = client.get('/api/workout-stats')
    data2 = json.loads(response2.data)
    updated_total = sum(data2['durations'])

    assert updated_total == initial_total + 30
