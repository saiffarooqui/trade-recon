import os

# Get the absolute path of the directory containing this file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # This will create 'trade_recon.db' inside the backend/app/ directory
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'trade_recon.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
