import pytest
from app import app as flask_app

@pytest.fixture(scope='module')
def app():
    """Create application for testing"""
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture(scope='module')
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()
