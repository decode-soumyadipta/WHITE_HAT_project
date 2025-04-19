from app.extensions import db
from datetime import datetime

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # e.g., "sql_injection", "xss", "csrf"
    target = db.Column(db.String(255))  # Target system/endpoint
    payload = db.Column(db.Text)  # The actual test payload
    expected_result = db.Column(db.Text)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    result = db.Column(db.Text)  # Results of the test
    vulnerability_id = db.Column(db.Integer, db.ForeignKey('vulnerability.id'), nullable=True)
    vulnerability = db.relationship('Vulnerability', backref='test_cases')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'target': self.target,
            'payload': self.payload,
            'expected_result': self.expected_result,
            'organization_id': self.organization_id,
            'status': self.status,
            'result': self.result,
            'vulnerability_id': self.vulnerability_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 