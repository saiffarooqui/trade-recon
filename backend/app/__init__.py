from flask import Flask
from flask_cors import CORS
from app.models import db
from app.config import Config


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    # Conditionally load configuration
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import recon_bp

    app.register_blueprint(recon_bp)

    return app
