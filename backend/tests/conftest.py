import pytest
from app import create_app
from app.models import db


@pytest.fixture
def app():
    """Creates a new Flask app instance for each test with an in-memory database."""
    # Pass the config directly into the app factory
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)

    with app.app_context():
        # Tables are already created in create_app, but we explicitly yield the app
        yield app

        # Teardown
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app to send HTTP requests."""
    return app.test_client()
