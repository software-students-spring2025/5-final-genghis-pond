import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.absolute()
web_app_path = project_root / "web_app"
sys.path.append(str(web_app_path))

import pytest
import tempfile
from datetime import datetime
from unittest.mock import patch
from core import create_app, mongo
from core.models.user import User
from core.models.sightings import Sighting

TEST_USERNAME = "humphrey"
TEST_EMAIL = "sigma@hotmail.com"
TEST_PASSWORD = "123"


@pytest.fixture
def app():
    upload_dir = tempfile.mkdtemp()
    # Create app with test config
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongodb://localhost:27017/genghis-pond-test',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': upload_dir,
        'SECRET_KEY': 'test_secret_key',
    })
    with app.app_context():
        mongo.db.users.delete_many({})
        mongo.db.sightings.delete_many({})
        mongo.db.votes.delete_many({})
        # Create test user
        user = User(username=TEST_USERNAME, email=TEST_EMAIL, password_hash=None)
        user.set_password(TEST_PASSWORD)
        user.save()
        yield app
        mongo.db.users.delete_many({})
        mongo.db.sightings.delete_many({})
        mongo.db.votes.delete_many({})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    client.post('/login', data={
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    })
    return client


@pytest.fixture
def test_user(app):
    with app.app_context():
        return User.get_by_email(TEST_EMAIL)


@pytest.fixture
def mock_s3_upload():
    with patch('core.routes.sightings.save_image') as mock:
        mock.return_value = 'http://fake-s3-bucket.s3.amazonaws.com/test_image.jpg'
        yield mock


@pytest.fixture
def mock_find_species():
    with patch('core.routes.sightings.find_species') as mock:
        mock.return_value = ('test_species', 0.95, 5)
        yield mock


@pytest.fixture
def mock_get_votes():
    with patch('core.models.sightings.Sighting.get_votes') as mock:
        mock.return_value = ({'test_species': 100.0}, 1)  # Return a tuple with a dict and count
        yield mock


@pytest.fixture
def test_sighting(app, test_user):
    with app.app_context():
        mongo.db.votes.insert_one({
            'sighting_id': 'test_sighting_id',
            'user_id': test_user.id,
            'species_guess': 'test_species',
            'confidence_level': 5
        })
        sighting = Sighting(
            species="test_species",
            description="Test description",
            latitude=40.7128,
            longitude=-74.0060,
            user_id=test_user.id,
            image_file="http://example.com/test.jpg",
            date_posted=datetime.now().replace(microsecond=0)
        )
        sighting.save()
        mongo.db.votes.update_one(
            {'sighting_id': 'test_sighting_id'},
            {'$set': {'sighting_id': sighting.id}}
        )
        yield sighting