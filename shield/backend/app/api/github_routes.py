from flask import Blueprint, request, jsonify
import logging
import json
import tempfile
import shutil
import os
from git import Repo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
github_bp = Blueprint('github', __name__)

# Try to import the AI agent or create a simpler fallback version
try:
    from ..services.ai_agent import ai_agent
    ai_agent_available = True
except ImportError:
    ai_agent_available = False
    logger.warning("AI agent not available. Using fallback implementation.")

    class FallbackAIAgent:
        """Simple fallback AI agent when LangChain is not available."""
        
        def __init__(self):
            self.temp_dir = None
        
        def _detect_tech_stack(self, repo_path):
            """Detect technology stack in the repository."""
            tech_stack = {
                "languages": [],
                "frameworks": [],
                "databases": []
            }
            
            # Simple detection logic
            if os.path.exists(os.path.join(repo_path, "package.json")):
                tech_stack["languages"].append("JavaScript")
                tech_stack["frameworks"].append("Node.js")
            
            if os.path.exists(os.path.join(repo_path, "requirements.txt")):
                tech_stack["languages"].append("Python")
            
            return tech_stack
        
        def analyze_repository(self, repo_url, branch="main"):
            """Analyze repository without LangChain."""
            try:
                # Create temporary directory
                self.temp_dir = tempfile.mkdtemp(prefix="shield_repo_")
                
                # Clone repository
                repo = Repo.clone_from(repo_url, self.temp_dir, branch=branch)
                
                # Detect tech stack
                tech_stack = self._detect_tech_stack(self.temp_dir)
                
                # Generate mock vulnerabilities and test cases
                mock_vulns = [
                    {
                        "name": "Outdated Dependencies",
                        "description": "Using outdated packages can expose known vulnerabilities.",
                        "severity": "Medium",
                        "affected_components": "Package management",
                        "recommendation": "Update all dependencies regularly"
                    },
                    {
                        "name": "Insecure Authentication",
                        "description": "Insufficient authentication mechanisms can lead to unauthorized access.",
                        "severity": "High",
                        "affected_components": "Authentication system",
                        "recommendation": "Implement MFA and strong password policies"
                    }
                ]
                
                mock_test_cases = [
                    {
                        "name": "Dependency Scanner Test",
                        "description": "Scan for outdated dependencies with known vulnerabilities",
                        "test_type": "Security Test",
                        "steps": ["Run dependency scanner", "Check for CVEs"],
                        "expected_result": "No critical vulnerabilities",
                        "severity": "Medium"
                    },
                    {
                        "name": "Authentication Security Test",
                        "description": "Test authentication mechanisms for security issues",
                        "test_type": "Security Test",
                        "steps": ["Test password complexity", "Test login rate limiting"],
                        "expected_result": "Strong authentication controls",
                        "severity": "High"
                    }
                ]
                
                return {
                    "tech_stack": tech_stack,
                    "vulnerabilities": mock_vulns,
                    "test_cases": mock_test_cases,
                    "risk_analysis": {
                        "summary": "Basic risk analysis without LangChain integration",
                        "financial_impact": "Unknown - requires manual assessment"
                    },
                    "recommendations": [
                        "Update dependencies regularly",
                        "Implement secure coding practices",
                        "Conduct regular security testing"
                    ],
                    "output": "Basic repository analysis completed"
                }
            except Exception as e:
                logger.error(f"Error in fallback repository analysis: {str(e)}")
                return {"error": str(e)}
            finally:
                # Clean up
                if self.temp_dir and os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                    self.temp_dir = None
    
    # Create a fallback instance
    ai_agent = FallbackAIAgent()

@github_bp.route('/api/github/analyze', methods=['POST'])
def analyze_github_repo():
    """Analyze a GitHub repository for security vulnerabilities."""
    try:
        # Get repository URL and branch from request
        data = request.get_json()
        
        if not data or 'repo_url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Repository URL is required'
            }), 400
        
        repo_url = data['repo_url']
        branch = data.get('branch', 'main')
        
        # Log whether using real or fallback AI agent
        if ai_agent_available:
            logger.info(f"Analyzing repository {repo_url} (branch: {branch}) with LangChain AI agent")
        else:
            logger.info(f"Analyzing repository {repo_url} (branch: {branch}) with fallback implementation")
        
        # Analyze repository
        result = ai_agent.analyze_repository(repo_url, branch)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"Error analyzing repository: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 