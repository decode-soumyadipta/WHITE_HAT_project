import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration for Flask application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key-change-in-production'
    
    # Use SQLite database by default, can be overridden by DATABASE_URL environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shield.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API key for AI functionality
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Database initialization settings
    INITIALIZE_TEST_DATA = True 