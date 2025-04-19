from flask import Blueprint, request, jsonify
from app.models import Organization, Vulnerability, TestCase
from app.extensions import db
from app.services.threat_intelligence import analyze_threats
from app.services.test_case_generator import generate_test_cases
from app.services.attack_simulator import simulate_attacks
from app.services.risk_analyzer import analyze_risk
import json

api_bp = Blueprint('api', __name__)

# Organization routes
@api_bp.route('/organizations', methods=['GET'])
def get_organizations():
    organizations = Organization.query.all()
    return jsonify([org.to_dict() for org in organizations])

@api_bp.route('/organizations/<int:id>', methods=['GET'])
def get_organization(id):
    organization = Organization.query.get_or_404(id)
    return jsonify(organization.to_dict())

@api_bp.route('/organizations', methods=['POST'])
def create_organization():
    data = request.get_json() or {}
    organization = Organization(
        name=data.get('name'),
        description=data.get('description'),
        industry=data.get('industry'),
        tech_stack=json.dumps(data.get('tech_stack', []))
    )
    db.session.add(organization)
    db.session.commit()
    return jsonify(organization.to_dict()), 201

# Vulnerability routes
@api_bp.route('/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    org_id = request.args.get('organization_id', type=int)
    query = Vulnerability.query
    if org_id:
        query = query.filter_by(organization_id=org_id)
    vulnerabilities = query.all()
    return jsonify([vuln.to_dict() for vuln in vulnerabilities])

@api_bp.route('/vulnerabilities/<int:id>', methods=['GET'])
def get_vulnerability(id):
    vulnerability = Vulnerability.query.get_or_404(id)
    return jsonify(vulnerability.to_dict())

@api_bp.route('/vulnerabilities', methods=['POST'])
def create_vulnerability():
    data = request.get_json() or {}
    vulnerability = Vulnerability(
        title=data.get('title'),
        description=data.get('description'),
        cvss_score=data.get('cvss_score'),
        status=data.get('status', 'open'),
        severity=data.get('severity'),
        affected_systems=json.dumps(data.get('affected_systems', [])),
        business_impact=data.get('business_impact'),
        remediation_plan=data.get('remediation_plan'),
        organization_id=data.get('organization_id')
    )
    db.session.add(vulnerability)
    db.session.commit()
    return jsonify(vulnerability.to_dict()), 201

# Test Case routes
@api_bp.route('/test-cases', methods=['GET'])
def get_test_cases():
    org_id = request.args.get('organization_id', type=int)
    vuln_id = request.args.get('vulnerability_id', type=int)
    
    query = TestCase.query
    if org_id:
        query = query.filter_by(organization_id=org_id)
    if vuln_id:
        query = query.filter_by(vulnerability_id=vuln_id)
        
    test_cases = query.all()
    return jsonify([tc.to_dict() for tc in test_cases])

@api_bp.route('/test-cases/<int:id>', methods=['GET'])
def get_test_case(id):
    test_case = TestCase.query.get_or_404(id)
    return jsonify(test_case.to_dict())

@api_bp.route('/test-cases', methods=['POST'])
def create_test_case():
    data = request.get_json() or {}
    test_case = TestCase(
        name=data.get('name'),
        description=data.get('description'),
        type=data.get('type'),
        target=data.get('target'),
        payload=data.get('payload'),
        expected_result=data.get('expected_result'),
        organization_id=data.get('organization_id'),
        vulnerability_id=data.get('vulnerability_id')
    )
    db.session.add(test_case)
    db.session.commit()
    return jsonify(test_case.to_dict()), 201

# AI Service routes
@api_bp.route('/analyze-threats', methods=['POST'])
def threat_analysis_endpoint():
    data = request.get_json() or {}
    org_id = data.get('organization_id')
    tech_stack = data.get('tech_stack')
    
    if not org_id or not tech_stack:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    results = analyze_threats(org_id, tech_stack)
    return jsonify(results)

@api_bp.route('/generate-test-cases', methods=['POST'])
def test_case_generation_endpoint():
    data = request.get_json() or {}
    org_id = data.get('organization_id')
    vulnerability_types = data.get('vulnerability_types', [])
    tech_stack = data.get('tech_stack')
    
    if not org_id or not tech_stack:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    results = generate_test_cases(org_id, tech_stack, vulnerability_types)
    return jsonify(results)

@api_bp.route('/simulate-attack', methods=['POST'])
def attack_simulation_endpoint():
    data = request.get_json() or {}
    test_case_id = data.get('test_case_id')
    
    if not test_case_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    results = simulate_attacks(test_case_id)
    return jsonify(results)

@api_bp.route('/analyze-risk', methods=['POST'])
def risk_analysis_endpoint():
    data = request.get_json() or {}
    vuln_id = data.get('vulnerability_id')
    
    if not vuln_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    results = analyze_risk(vuln_id)
    return jsonify(results)

@api_bp.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    org_id = request.args.get('organization_id', type=int)
    if not org_id:
        return jsonify({'error': 'Missing organization ID'}), 400
    
    # Get vulnerability counts by severity
    vuln_by_severity = {}
    severities = ['critical', 'high', 'medium', 'low']
    for severity in severities:
        count = Vulnerability.query.filter_by(organization_id=org_id, severity=severity).count()
        vuln_by_severity[severity] = count
    
    # Get test case statistics
    test_case_stats = {
        'total': TestCase.query.filter_by(organization_id=org_id).count(),
        'pending': TestCase.query.filter_by(organization_id=org_id, status='pending').count(),
        'running': TestCase.query.filter_by(organization_id=org_id, status='running').count(),
        'completed': TestCase.query.filter_by(organization_id=org_id, status='completed').count(),
        'failed': TestCase.query.filter_by(organization_id=org_id, status='failed').count()
    }
    
    # Get recent vulnerabilities
    recent_vulns = Vulnerability.query.filter_by(organization_id=org_id).order_by(Vulnerability.discovered_at.desc()).limit(5).all()
    
    return jsonify({
        'vulnerability_by_severity': vuln_by_severity,
        'test_case_stats': test_case_stats,
        'recent_vulnerabilities': [v.to_dict() for v in recent_vulns]
    }) 