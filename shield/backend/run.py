from app import create_app, db
from app.models.user import User
from app.models.organization import Organization
from app.models.vulnerability import Vulnerability
from app.models.test_case import TestCase
from flask_cors import CORS
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}})

def initialize_database():
    """Initialize database with initial data"""
    try:
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Create a test user if it doesn't exist
        if app.config.get('INITIALIZE_TEST_DATA', True):
            if not User.query.filter_by(email='admin@shield.com').first():
                test_user = User(
                    username='admin',
                    email='admin@shield.com',
                    role='admin'
                )
                test_user.set_password('admin123')
                db.session.add(test_user)
                
                # Create a test organization
                test_org = Organization(
                    name='Test Organization',
                    industry='Technology',
                    tech_stack='{"languages": ["Python", "JavaScript"], "frameworks": ["Flask", "React"]}'
                )
                db.session.add(test_org)
                db.session.commit()
                logger.info("Initialized database with test data")
            else:
                logger.info("Test data already exists in database")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Organization': Organization,
        'Vulnerability': Vulnerability,
        'TestCase': TestCase
    }

if __name__ == '__main__':
    # Ensure the application context is active before accessing the database
    with app.app_context():
        if not initialize_database():
            logger.warning("Continuing without test data - some features may not work properly")
    
    # Set the host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Run the application
    logger.info(f"Starting Shield API server on http://{host}:{port}")
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"Error starting server: {e}") 