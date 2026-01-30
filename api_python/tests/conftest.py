import os
import pytest

os.environ.setdefault('API_KEY', '2f5ae96c-b558-4c7b-a590-a501ae1c3f6c')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('JWT_EXPIRATION_HOURS', '1')

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_api_key():
    return os.environ['API_KEY']


@pytest.fixture
def valid_payload():
    return {
        "message": "This is a test",
        "to": "Juan Perez",
        "from": "Rita Asturia",
        "timeToLifeSec": 45
    }


@pytest.fixture
def valid_headers(valid_api_key):
    return {
        'Content-Type': 'application/json',
        'X-Parse-REST-API-Key': valid_api_key
    }
