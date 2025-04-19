"""
Simple API for testing the AI security agent.
"""
from flask import Blueprint, request, jsonify
import logging
from ..services.agent_builder import security_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
test_agent_bp = Blueprint('test_agent', __name__)

@test_agent_bp.route('/api/test-agent/analyze', methods=['POST'])
def analyze_tech_stack():
    """Analyze a technology stack for security vulnerabilities."""
    try:
        # Get tech stack from request
        data = request.get_json()
        
        if not data or 'technologies' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Technologies list is required'
            }), 400
        
        tech_stack = data['technologies']
        
        # Log the request
        logger.info(f"Analyzing tech stack: {tech_stack}")
        
        # Analyze the tech stack
        result = security_agent.analyze_repository_security(tech_stack)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"Error analyzing tech stack: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 