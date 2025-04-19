import os
import json
import logging
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from git import Repo
import requests

from ..models.organization import Organization
from ..models.vulnerability import Vulnerability
from ..models.test_case import TestCase
from .agent_builder import SecurityAgent
from ..services.test_case_generator import TestCaseGeneratorService
from ..services.attack_simulator import AttackSimulatorService
from ..services.risk_analyzer import RiskAnalyzerService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AISecurityAgent:
    """AI Security Agent for GitHub repository analysis."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize services
        self.security_agent = SecurityAgent()  # Our new agent implementation
        self.test_case_generator = TestCaseGeneratorService()
        self.attack_simulator = AttackSimulatorService()
        self.risk_analyzer = RiskAnalyzerService()
        
        # Temporary directory for repository cloning
        self.temp_dir = None
    
    def _detect_technologies(self, repo_path):
        """Detect technologies used in the repository."""
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_services": [],
            "other_dependencies": []
        }
        
        try:
            # Look for package.json (Node.js/JavaScript)
            if os.path.exists(os.path.join(repo_path, "package.json")):
                tech_stack["languages"].append("JavaScript/TypeScript")
                with open(os.path.join(repo_path, "package.json")) as f:
                    pkg_data = json.load(f)
                    dependencies = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    
                    # Detect frameworks
                    if "react" in dependencies:
                        tech_stack["frameworks"].append("React")
                    if "vue" in dependencies:
                        tech_stack["frameworks"].append("Vue.js")
                    if "express" in dependencies:
                        tech_stack["frameworks"].append("Express.js")
            
            # Look for requirements.txt (Python)
            if os.path.exists(os.path.join(repo_path, "requirements.txt")):
                tech_stack["languages"].append("Python")
                with open(os.path.join(repo_path, "requirements.txt")) as f:
                    requirements = f.read().lower()
                    
                    if "django" in requirements:
                        tech_stack["frameworks"].append("Django")
                    if "flask" in requirements:
                        tech_stack["frameworks"].append("Flask")
                    if "sqlalchemy" in requirements:
                        tech_stack["frameworks"].append("SQLAlchemy")
            
            # Look for pom.xml (Java/Maven)
            if os.path.exists(os.path.join(repo_path, "pom.xml")):
                tech_stack["languages"].append("Java")
                tech_stack["frameworks"].append("Maven")
            
            # Look for Gemfile (Ruby)
            if os.path.exists(os.path.join(repo_path, "Gemfile")):
                tech_stack["languages"].append("Ruby")
                with open(os.path.join(repo_path, "Gemfile")) as f:
                    gemfile = f.read().lower()
                    
                    if "rails" in gemfile:
                        tech_stack["frameworks"].append("Ruby on Rails")
            
            # Detect Docker usage
            if os.path.exists(os.path.join(repo_path, "Dockerfile")) or os.path.exists(os.path.join(repo_path, "docker-compose.yml")):
                tech_stack["other_dependencies"].append("Docker")
            
            # Detect database connections
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.rb')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                            # Check for database mentions
                            if 'mongodb' in content:
                                if 'mongodb' not in tech_stack["databases"]:
                                    tech_stack["databases"].append("MongoDB")
                            if 'postgresql' in content or 'postgres' in content:
                                if 'postgresql' not in tech_stack["databases"]:
                                    tech_stack["databases"].append("PostgreSQL")
                            if 'mysql' in content:
                                if 'mysql' not in tech_stack["databases"]:
                                    tech_stack["databases"].append("MySQL")
                            
                            # Check for cloud services
                            if 'aws' in content or 'amazon' in content:
                                if 'aws' not in tech_stack["cloud_services"]:
                                    tech_stack["cloud_services"].append("AWS")
                            if 'azure' in content:
                                if 'azure' not in tech_stack["cloud_services"]:
                                    tech_stack["cloud_services"].append("Azure")
                            if 'gcp' in content or 'google cloud' in content:
                                if 'gcp' not in tech_stack["cloud_services"]:
                                    tech_stack["cloud_services"].append("Google Cloud")
            
            return tech_stack
        except Exception as e:
            logger.error(f"Error detecting technologies: {str(e)}")
            return tech_stack
    
    def _generate_security_analysis(self, tech_stack):
        """Generate security analysis based on technology stack using our new agent."""
        try:
            # Convert tech_stack dictionary to a flat list
            all_technologies = []
            for category, items in tech_stack.items():
                all_technologies.extend(items)
            
            # Use our SecurityAgent to analyze the technologies
            analysis = self.security_agent.analyze_repository_security(all_technologies)
            
            # Format the result to match the expected structure
            result = {
                "vulnerabilities": analysis.get("vulnerabilities", []),
                "test_cases": [],
                "risk_analysis": analysis.get("risk_assessment", {}),
                "recommendations": analysis.get("risk_assessment", {}).get("recommendations", []),
                "tech_stack": tech_stack
            }
            
            # Extract test cases from vulnerabilities
            for vuln in analysis.get("vulnerabilities", []):
                if "detailed_test_cases" in vuln:
                    for test_case in vuln.get("detailed_test_cases", []):
                        result["test_cases"].append({
                            "name": test_case.get("name", ""),
                            "description": test_case.get("description", ""),
                            "steps": test_case.get("steps", []),
                            "vulnerability": vuln.get("title", ""),
                            "severity": vuln.get("severity", "")
                        })
            
            return result
        except Exception as e:
            logger.error(f"Error generating security analysis: {str(e)}")
            # Return simplified analysis
            return {
                "vulnerabilities": [],
                "test_cases": [],
                "risk_analysis": {
                    "summary": "Error generating risk analysis."
                },
                "recommendations": ["Consult with a security expert."],
                "tech_stack": tech_stack,
                "error": str(e)
            }
    
    def analyze_repository(self, repo_url, branch="main"):
        """Analyze a GitHub repository for security vulnerabilities."""
        try:
            # Create a temporary directory for the repository
            self.temp_dir = tempfile.mkdtemp(prefix="shield_repo_")
            logger.info(f"Created temporary directory: {self.temp_dir}")
            
            # Clone the repository
            logger.info(f"Cloning repository: {repo_url}, branch: {branch}")
            Repo.clone_from(repo_url, self.temp_dir, branch=branch)
            
            # Detect technologies
            logger.info("Detecting technologies...")
            tech_stack = self._detect_technologies(self.temp_dir)
            
            # Generate security analysis
            logger.info("Generating security analysis...")
            analysis = self._generate_security_analysis(tech_stack)
            analysis["tech_stack"] = tech_stack
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            return {"error": str(e)}
        finally:
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                logger.info("Cleaned up temporary directory")

# Create a singleton instance
ai_agent = AISecurityAgent() 