from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../../frontend/build', static_url_path='/')
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.api.routes import api_bp
    from app.auth.routes import auth_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return app.send_static_file(path)
        return app.send_static_file('index.html')
    
    return app 