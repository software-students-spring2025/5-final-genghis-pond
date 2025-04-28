import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from web_app.core import create_app
import tempfile

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        # temp folder for testing uoloads
        "UPLOAD_FOLDER": tempfile.mkdtemp(),
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
