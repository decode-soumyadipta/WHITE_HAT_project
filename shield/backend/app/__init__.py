from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from app.routes import auth, dashboard, vulnerabilities, test_cases
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(vulnerabilities.bp)
    app.register_blueprint(test_cases.bp)
    
    # Register GitHub API routes
    try:
        from app.api.github_routes import github_bp
        app.register_blueprint(github_bp)
    except ImportError as e:
        print(f"Warning: Could not import github_bp: {e}")
        print("GitHub repository analysis features will be disabled.")
    
    # Register test agent API routes
    try:
        from app.api.test_agent_api import test_agent_bp
        app.register_blueprint(test_agent_bp)
        print("Test agent API routes registered successfully.")
    except ImportError as e:
        print(f"Warning: Could not import test_agent_bp: {e}")
        print("Test agent API features will be disabled.")

    # API Root route
    @app.route('/')
    def api_root():
        return jsonify({
            'status': 'success',
            'message': 'Shield API is running',
            'api_version': '1.0',
            'endpoints': [
                '/api/github/analyze',
                '/api/test-agent/analyze',
                '/api/auth/*',
                '/api/vulnerabilities/*',
                '/api/test-cases/*'
            ]
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'error': str(e)
        }), 404

    return app 