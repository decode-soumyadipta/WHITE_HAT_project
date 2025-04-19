from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../../frontend/build', static_url_path='')
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from app.routes import auth, dashboard, vulnerabilities, test_cases
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(vulnerabilities.bp)
    app.register_blueprint(test_cases.bp)

    # Serve React App
    @app.route('/')
    def serve():
        return send_from_directory(app.static_folder, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory(app.static_folder, 'index.html')

    return app 