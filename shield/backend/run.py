from app import create_app
from app.extensions import db
from app.models import User, Organization, Vulnerability, TestCase

app = create_app()

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
    app.run(debug=True, host='0.0.0.0', port=5000) 