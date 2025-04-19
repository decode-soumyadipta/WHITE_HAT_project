from flask import Blueprint, jsonify, request
from app.models.test_case import TestCase
from app.models.organization import Organization
from app.extensions import db
import json

bp = Blueprint('test_cases', __name__)

@bp.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """Get all test cases."""
    test_cases = TestCase.query.all()
    
    # Convert test cases to a list of dictionaries
    result = []
    for tc in test_cases:
        org = Organization.query.get(tc.organization_id)
        tc_data = {
            'id': tc.id,
            'name': tc.name,
            'description': tc.description,
            'test_type': tc.test_type,
            'status': tc.status,
            'organization_id': tc.organization_id,
            'organization_name': org.name if org else 'Unknown',
            'created_at': tc.created_at.isoformat() if tc.created_at else None,
            'updated_at': tc.updated_at.isoformat() if tc.updated_at else None
        }
        result.append(tc_data)
    
    return jsonify(result)

@bp.route('/api/test-cases/<int:id>', methods=['GET'])
def get_test_case(id):
    """Get a specific test case."""
    tc = TestCase.query.get_or_404(id)
    org = Organization.query.get(tc.organization_id)
    
    result = {
        'id': tc.id,
        'name': tc.name,
        'description': tc.description,
        'test_type': tc.test_type,
        'status': tc.status,
        'organization_id': tc.organization_id,
        'organization_name': org.name if org else 'Unknown',
        'created_at': tc.created_at.isoformat() if tc.created_at else None,
        'updated_at': tc.updated_at.isoformat() if tc.updated_at else None,
        'parameters': json.loads(tc.parameters) if tc.parameters else {}
    }
    
    return jsonify(result)

@bp.route('/api/test-cases', methods=['POST'])
def create_test_case():
    """Create a new test case."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'organization_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create test case
    tc = TestCase(
        name=data['name'],
        description=data['description'],
        test_type=data.get('test_type', 'Manual Test'),
        status=data.get('status', 'Pending'),
        organization_id=data['organization_id'],
        parameters=data.get('parameters', '{}')
    )
    
    db.session.add(tc)
    db.session.commit()
    
    return jsonify({'id': tc.id, 'message': 'Test case created successfully'}), 201

@bp.route('/api/test-cases/<int:id>', methods=['PUT'])
def update_test_case(id):
    """Update a test case."""
    tc = TestCase.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        tc.name = data['name']
    if 'description' in data:
        tc.description = data['description']
    if 'test_type' in data:
        tc.test_type = data['test_type']
    if 'status' in data:
        tc.status = data['status']
    if 'organization_id' in data:
        tc.organization_id = data['organization_id']
    if 'parameters' in data:
        tc.parameters = data['parameters']
    
    db.session.commit()
    
    return jsonify({'message': 'Test case updated successfully'})

@bp.route('/api/organizations', methods=['GET'])
def get_organizations():
    """Get all organizations."""
    orgs = Organization.query.all()
    result = []
    
    for org in orgs:
        org_data = {
            'id': org.id,
            'name': org.name,
            'industry': org.industry,
            'created_at': org.created_at.isoformat() if org.created_at else None
        }
        result.append(org_data)
    
    return jsonify(result) 