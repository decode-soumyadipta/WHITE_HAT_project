from flask import Blueprint, jsonify, request
from app.models.vulnerability import Vulnerability
from app.models.organization import Organization
from app.extensions import db
import json

bp = Blueprint('vulnerabilities', __name__)

@bp.route('/api/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    """Get all vulnerabilities."""
    vulnerabilities = Vulnerability.query.all()
    
    # Convert vulnerabilities to a list of dictionaries
    result = []
    for vuln in vulnerabilities:
        org = Organization.query.get(vuln.organization_id)
        vuln_data = {
            'id': vuln.id,
            'name': vuln.name,
            'description': vuln.description,
            'severity': vuln.severity,
            'status': vuln.status,
            'affected_components': vuln.affected_components,
            'remediation': vuln.remediation,
            'organization_id': vuln.organization_id,
            'organization_name': org.name if org else 'Unknown',
            'created_at': vuln.created_at.isoformat() if vuln.created_at else None,
            'updated_at': vuln.updated_at.isoformat() if vuln.updated_at else None
        }
        result.append(vuln_data)
    
    return jsonify(result)

@bp.route('/api/vulnerabilities/<int:id>', methods=['GET'])
def get_vulnerability(id):
    """Get a specific vulnerability."""
    vuln = Vulnerability.query.get_or_404(id)
    org = Organization.query.get(vuln.organization_id)
    
    result = {
        'id': vuln.id,
        'name': vuln.name,
        'description': vuln.description,
        'severity': vuln.severity,
        'status': vuln.status,
        'affected_components': vuln.affected_components,
        'remediation': vuln.remediation,
        'organization_id': vuln.organization_id,
        'organization_name': org.name if org else 'Unknown',
        'created_at': vuln.created_at.isoformat() if vuln.created_at else None,
        'updated_at': vuln.updated_at.isoformat() if vuln.updated_at else None,
        'details': json.loads(vuln.details) if vuln.details else {}
    }
    
    return jsonify(result)

@bp.route('/api/vulnerabilities', methods=['POST'])
def create_vulnerability():
    """Create a new vulnerability."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'severity', 'organization_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create vulnerability
    vuln = Vulnerability(
        name=data['name'],
        description=data['description'],
        severity=data['severity'],
        status=data.get('status', 'Open'),
        affected_components=data.get('affected_components', ''),
        remediation=data.get('remediation', ''),
        organization_id=data['organization_id'],
        details=json.dumps(data.get('details', {}))
    )
    
    db.session.add(vuln)
    db.session.commit()
    
    return jsonify({'id': vuln.id, 'message': 'Vulnerability created successfully'}), 201

@bp.route('/api/vulnerabilities/<int:id>', methods=['PUT'])
def update_vulnerability(id):
    """Update a vulnerability."""
    vuln = Vulnerability.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        vuln.name = data['name']
    if 'description' in data:
        vuln.description = data['description']
    if 'severity' in data:
        vuln.severity = data['severity']
    if 'status' in data:
        vuln.status = data['status']
    if 'affected_components' in data:
        vuln.affected_components = data['affected_components']
    if 'remediation' in data:
        vuln.remediation = data['remediation']
    if 'organization_id' in data:
        vuln.organization_id = data['organization_id']
    if 'details' in data:
        vuln.details = json.dumps(data['details'])
    
    db.session.commit()
    
    return jsonify({'message': 'Vulnerability updated successfully'}) 