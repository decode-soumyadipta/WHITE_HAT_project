"""
Database and extension configuration for the Flask application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create a shared SQLAlchemy instance to be used throughout the application
db = SQLAlchemy()
migrate = Migrate() 