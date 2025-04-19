from flask import Blueprint, request, jsonify, current_app, url_for, redirect, session
from app.models.organization import Organization
from app.models.vulnerability import Vulnerability
from app.models.test_case import TestCase
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.services.threat_intelligence import analyze_threat_intelligence
from app.services.test_case_generator import generate_test_cases
from app.services.attack_simulator import simulate_attacks
from app.services.risk_analyzer import analyze_risk
from datetime import datetime, timedelta
import requests
import os
import json
import uuid

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
    
    results = analyze_threat_intelligence(org_id, tech_stack)
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

# AI Agent Automation endpoints
@api_bp.route('/ai-agent-assessment', methods=['POST'])
def ai_agent_assessment_endpoint():
    """
    Run an automated security assessment using AI agents
    """
    from app.services.ai_agent_automation import AIAgentManager
    
    data = request.get_json() or {}
    org_id = data.get('organization_id')
    tech_stack = data.get('tech_stack')
    assessment_type = data.get('assessment_type')
    
    if not org_id or not tech_stack:
        return jsonify({'error': 'Missing required parameters (organization_id, tech_stack)'}), 400
    
    # Create AI Agent Manager and run assessment
    agent_manager = AIAgentManager(org_id)
    results = agent_manager.run_automated_assessment(tech_stack, assessment_type)
    
    return jsonify(results)

@api_bp.route('/ai-agent-test-cases/<int:org_id>', methods=['GET'])
def ai_agent_test_cases(org_id):
    """
    Get all test cases generated by AI agents for an organization
    """
    # Query test cases created by AI agents
    test_cases = TestCase.query.filter_by(
        organization_id=org_id,
    ).order_by(TestCase.created_at.desc()).all()
    
    return jsonify([tc.to_dict() for tc in test_cases])

@api_bp.route('/ai-agent-vulnerabilities/<int:org_id>', methods=['GET'])
def ai_agent_vulnerabilities(org_id):
    """
    Get all vulnerabilities discovered by AI agents for an organization
    """
    # Query vulnerabilities discovered by AI agents
    vulnerabilities = Vulnerability.query.filter_by(
        organization_id=org_id,
        discovered_by='SHIELD AI Agent'
    ).order_by(Vulnerability.discovered_at.desc()).all()
    
    return jsonify([vuln.to_dict() for vuln in vulnerabilities])

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

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'your-github-client-id')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', 'your-github-client-secret')
GITHUB_CALLBACK_URL = os.environ.get('GITHUB_CALLBACK_URL', 'http://localhost:5000/api/auth/github/callback')

@api_bp.route('/auth/github', methods=['GET'])
@jwt_required()
def github_auth():
    """Initiate GitHub OAuth flow"""
    user_id = get_jwt_identity()
    
    # Store the user ID in session for the callback
    session['user_id'] = user_id
    
    # Define GitHub OAuth parameters
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_CALLBACK_URL,
        'scope': 'user:email repo read:org',
        'state': str(uuid.uuid4())
    }
    
    # Store state in session to prevent CSRF
    session['github_oauth_state'] = params['state']
    
    # Redirect user to GitHub for authorization
    github_auth_url = f"https://github.com/login/oauth/authorize?{'&'.join(f'{key}={value}' for key, value in params.items())}"
    return jsonify({'auth_url': github_auth_url})

@api_bp.route('/auth/github/callback', methods=['GET'])
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state to prevent CSRF
    if state != session.get('github_oauth_state'):
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    # Get user_id from session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user session found'}), 401
    
    # Exchange code for access token
    token_url = 'https://github.com/login/oauth/access_token'
    payload = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_CALLBACK_URL
    }
    headers = {'Accept': 'application/json'}
    
    response = requests.post(token_url, data=payload, headers=headers)
    token_data = response.json()
    
    if 'error' in token_data:
        return jsonify({'error': token_data['error_description']}), 400
    
    access_token = token_data.get('access_token')
    
    # Get user info from GitHub
    github_user_url = 'https://api.github.com/user'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/json'
    }
    
    github_user_response = requests.get(github_user_url, headers=headers)
    github_user_data = github_user_response.json()
    
    # Get user emails from GitHub
    github_emails_url = 'https://api.github.com/user/emails'
    github_emails_response = requests.get(github_emails_url, headers=headers)
    github_emails = github_emails_response.json()
    
    # Find primary email
    primary_email = next((email['email'] for email in github_emails if email['primary']), None)
    
    # Update user with GitHub info
    user = User.query.get(user_id)
    if user:
        user.github_id = str(github_user_data.get('id'))
        user.github_username = github_user_data.get('login')
        user.github_access_token = access_token
        user.github_avatar_url = github_user_data.get('avatar_url')
        user.github_connected_at = datetime.utcnow()
        
        # If user doesn't have an email yet, use primary GitHub email
        if not user.email and primary_email:
            user.email = primary_email
            
        db.session.commit()
        
        # Create a new token with updated user info
        access_token = create_access_token(identity=user.id)
        
        # Redirect to frontend with the token
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/profile?github_connected=true&token={access_token}")
    
    return jsonify({'error': 'User not found'}), 404

@api_bp.route('/auth/github/disconnect', methods=['POST'])
@jwt_required()
def github_disconnect():
    """Disconnect user from GitHub"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Revoke GitHub access token if it exists
    if user.github_access_token:
        revoke_url = f'https://api.github.com/applications/{GITHUB_CLIENT_ID}/grant'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {GITHUB_CLIENT_ID}:{GITHUB_CLIENT_SECRET}'
        }
        payload = {'access_token': user.github_access_token}
        requests.delete(revoke_url, headers=headers, json=payload)
    
    # Clear GitHub fields
    user.github_id = None
    user.github_username = None
    user.github_access_token = None
    user.github_avatar_url = None
    user.github_connected_at = None
    
    db.session.commit()
    
    return jsonify({'message': 'Successfully disconnected from GitHub'})

@api_bp.route('/github/repositories', methods=['GET'])
@jwt_required()
def get_github_repositories():
    """Get user's GitHub repositories"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.github_access_token:
        return jsonify({'error': 'No GitHub connection found'}), 400
    
    # Get repositories from GitHub
    github_repos_url = 'https://api.github.com/user/repos'
    headers = {
        'Authorization': f'token {user.github_access_token}',
        'Accept': 'application/json'
    }
    params = {
        'sort': 'updated',
        'per_page': 100  # Adjust as needed
    }
    
    github_repos_response = requests.get(github_repos_url, headers=headers, params=params)
    
    if github_repos_response.status_code != 200:
        return jsonify({'error': 'Failed to fetch GitHub repositories'}), 400
    
    repos = github_repos_response.json()
    
    # Format repository data
    formatted_repos = [{
        'id': repo.get('id'),
        'name': repo.get('name'),
        'full_name': repo.get('full_name'),
        'description': repo.get('description'),
        'html_url': repo.get('html_url'),
        'private': repo.get('private'),
        'language': repo.get('language'),
        'updated_at': repo.get('updated_at'),
        'pushed_at': repo.get('pushed_at'),
        'default_branch': repo.get('default_branch')
    } for repo in repos]
    
    return jsonify({'repositories': formatted_repos}) 