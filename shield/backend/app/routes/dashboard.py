from flask import Blueprint, jsonify, session
from app.models.vulnerability import Vulnerability
from app.models.test_case import TestCase
from app.models.user import User
from sqlalchemy import func
import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/overview')
def get_overview():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    org_id = user.organization_id
    
    # Get vulnerability statistics
    vuln_stats = {
        'critical': Vulnerability.query.filter_by(organization_id=org_id, severity='critical').count(),
        'high': Vulnerability.query.filter_by(organization_id=org_id, severity='high').count(),
        'medium': Vulnerability.query.filter_by(organization_id=org_id, severity='medium').count(),
        'low': Vulnerability.query.filter_by(organization_id=org_id, severity='low').count()
    }
    
    # Get test case statistics
    test_stats = {
        'total': TestCase.query.filter_by(organization_id=org_id).count(),
        'passed': TestCase.query.filter_by(organization_id=org_id, status='completed').count(),
        'failed': TestCase.query.filter_by(organization_id=org_id, status='failed').count(),
        'pending': TestCase.query.filter_by(organization_id=org_id, status='pending').count()
    }
    
    # Get recent vulnerabilities
    recent_vulns = Vulnerability.query.filter_by(organization_id=org_id)\
        .order_by(Vulnerability.discovered_at.desc())\
        .limit(5)\
        .all()
    
    # Calculate risk score
    risk_score = calculate_risk_score(org_id)
    
    # Get vulnerability trends
    trends = get_vulnerability_trends(org_id)
    
    return jsonify({
        'vulnerability_stats': vuln_stats,
        'test_case_stats': test_stats,
        'recent_vulnerabilities': [v.to_dict() for v in recent_vulns],
        'risk_score': risk_score,
        'trends': trends
    })

def calculate_risk_score(org_id):
    vulnerabilities = Vulnerability.query.filter_by(organization_id=org_id).all()
    if not vulnerabilities:
        return 0
    
    weights = {
        'critical': 1.0,
        'high': 0.7,
        'medium': 0.4,
        'low': 0.1
    }
    
    total_score = sum(weights[v.severity] * v.cvss_score for v in vulnerabilities)
    max_possible = len(vulnerabilities) * 10  # Maximum CVSS score is 10
    
    return round((1 - (total_score / max_possible)) * 100, 2)

def get_vulnerability_trends(org_id):
    thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    
    vulnerabilities = Vulnerability.query\
        .filter(
            Vulnerability.organization_id == org_id,
            Vulnerability.discovered_at >= thirty_days_ago
        )\
        .all()
    
    # Group by date and severity
    trends = {}
    for vuln in vulnerabilities:
        date_key = vuln.discovered_at.strftime('%Y-%m-%d')
        if date_key not in trends:
            trends[date_key] = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        trends[date_key][vuln.severity] += 1
    
    return trends 