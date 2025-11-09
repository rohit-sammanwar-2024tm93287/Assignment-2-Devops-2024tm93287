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
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'ACEest Fitness' in response.data

def test_get_workouts_empty(client):
    """
    GIVEN a Flask application
    WHEN the '/api/workouts' endpoint is called (GET)
    THEN check that it returns an empty list initially
    """
    response = client.get('/api/workouts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'workouts' in data
    assert isinstance(data['workouts'], list)

def test_add_workout_success(client):
    """
    GIVEN a Flask application
    WHEN a new workout is posted to '/api/workouts'
    THEN check that it's added successfully
    """
    workout_data = {
        'workout': 'Push-ups',
        'duration': 30
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'Push-ups' in data['message']

def test_add_workout_missing_fields(client):
    """
    GIVEN a Flask application
    WHEN a workout is posted with missing fields
    THEN check that it returns an error
    """
    workout_data = {
        'workout': 'Push-ups'
        # Missing 'duration' field
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_add_workout_invalid_duration(client):
    """
    GIVEN a Flask application
    WHEN a workout is posted with invalid duration
    THEN check that it returns an error
    """
    workout_data = {
        'workout': 'Squats',
        'duration': 'invalid'
    }
    response = client.post('/api/workouts',
                           data=json.dumps(workout_data),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
