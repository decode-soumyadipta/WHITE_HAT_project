from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # GitHub integration fields
    github_id = db.Column(db.String(64), unique=True, nullable=True)
    github_username = db.Column(db.String(64), nullable=True)
    github_access_token = db.Column(db.String(128), nullable=True)
    github_avatar_url = db.Column(db.String(256), nullable=True)
    github_connected_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'organization_id': self.organization_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'github_connected': bool(self.github_id),
            'github_username': self.github_username,
            'github_avatar_url': self.github_avatar_url,
            'github_connected_at': self.github_connected_at.isoformat() if self.github_connected_at else None
        } 