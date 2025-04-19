from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.organization import Organization
from app.models.vulnerability import Vulnerability
from app.models.test_case import TestCase
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create a test user if it doesn't exist
    if not User.query.filter_by(email='admin@shield.com').first():
        test_user = User(
            username='admin',
            email='admin@shield.com',
            role='admin'
        )
        test_user.set_password('admin123')
        db.session.add(test_user)
        db.session.commit()

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
    with app.app_context():
        create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True) 