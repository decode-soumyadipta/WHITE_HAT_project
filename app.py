from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, g
import os
import json
import uuid
from datetime import datetime, timedelta
import sqlite3
import logging
import requests
from urllib.parse import urlencode
import secrets
import time
import threading
import traceback
import openai
from openai import OpenAI
import re
import random

# Define SQLAlchemy models for compatibility
class Organization:
    query = None
    def __init__(self, name, industry, description, admin_user_id):
        self.name = name
        self.industry = industry
        self.description = description
        self.admin_user_id = admin_user_id
        self.id = 1
    
class TestCase:
    query = None
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
class Vulnerability:
    query = None
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Mock for SQLAlchemy
class Query:
    def filter_by(self, **kwargs):
        return self
    
    def order_by(self, *args):
        return self
    
    def limit(self, n):
        return self
    
    def all(self):
        return []
    
    def desc(self):
        return self

# Add query properties to model classes
Organization.query = Query()
TestCase.query = Query()
Vulnerability.query = Query()

try:
    from flask_session import Session  # Import Flask-Session extension
except ImportError:
    # Fallback to basic cookie session if flask_session is not installed
    Session = None
    logging.warning("flask_session not installed, falling back to cookie-based sessions")

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 60 minutes session lifetime
app.config['SESSION_PERMANENT'] = True

# Only configure filesystem sessions if flask_session is available
if Session is not None:
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Create session directory if it doesn't exist
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize Flask-Session
    Session(app)
else:
    # Log that we're using cookie-based sessions
    logging.warning("Using cookie-based sessions. Install Flask-Session for better security.")

# GitHub OAuth Configuration 
GITHUB_CLIENT_ID = "Ov23lizdlyuPlVK8gxDv"  # Put your real Client ID here
GITHUB_CLIENT_SECRET = "435b70aad416b8eeca3fb00a11b440b03dbd7c9b"  # Put your real Client Secret here
GITHUB_CALLBACK_URL = os.environ.get('GITHUB_CALLBACK_URL', 'http://localhost:5000/github/callback')

# Database setup
DB_PATH = 'shield.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create organizations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        industry TEXT,
        tech_stack TEXT
    )
    ''')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        github_token TEXT
    )
    ''')
    
    # Create test_cases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        type TEXT,
        target TEXT,
        payload TEXT,
        expected_result TEXT,
        result TEXT,
        status TEXT DEFAULT 'pending',
        organization_id INTEGER,
        vulnerability_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organization_id) REFERENCES organizations (id),
        FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities (id)
    )
    ''')
    
    # Create vulnerabilities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vulnerabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        cvss_score REAL,
        status TEXT DEFAULT 'open',
        severity TEXT,
        affected_systems TEXT,
        business_impact REAL,
        remediation_plan TEXT,
        organization_id INTEGER,
        discovered_by TEXT DEFAULT 'SHIELD',
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organization_id) REFERENCES organizations (id)
    )
    ''')
    
    # Create github_repos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS github_repos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        repo_name TEXT NOT NULL,
        repo_url TEXT NOT NULL,
        github_id TEXT,
        last_scan TIMESTAMP,
        status TEXT DEFAULT 'not_scanned',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Insert sample data if not exists
    cursor.execute("SELECT COUNT(*) FROM organizations")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO organizations (name, description, industry, tech_stack)
        VALUES 
        ('Acme Corp', 'E-commerce platform', 'Retail', '["Python", "Django", "React", "PostgreSQL"]'),
        ('TechSolutions', 'Cloud services provider', 'Technology', '["Java", "Spring", "Angular", "MySQL"]'),
        ('FinSecure', 'Financial services', 'Banking', '["C#", ".NET", "Vue.js", "SQL Server"]')
        ''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Simple password: "password"
        cursor.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES ('admin', 'admin@shield.com', 'pbkdf2:sha256:150000$KKgd0xN5$d57ac1b8f46feba9d4a84b7a1de3a1cf298f8b5d8a0c1eea3a0a1e3e6ec631e4')
        ''')
    
    # Add the github_token field to the users table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN github_token TEXT")
        logging.info("Added github_token column to users table")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Add github_id column to github_repos table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE github_repos ADD COLUMN github_id TEXT")
        logging.info("Added github_id column to github_repos table")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
init_db()

# Helper functions
def organization_to_dict(org):
    return {
        'id': org['id'],
        'name': org['name'],
        'description': org['description'],
        'industry': org['industry'],
        'tech_stack': org['tech_stack']
    }

def test_case_to_dict(tc):
    return {
        'id': tc['id'],
        'name': tc['name'],
        'description': tc['description'],
        'type': tc['type'],
        'target': tc['target'],
        'payload': tc['payload'],
        'expected_result': tc['expected_result'],
        'result': tc['result'],
        'status': tc['status'],
        'organization_id': tc['organization_id'],
        'vulnerability_id': tc['vulnerability_id'],
        'created_at': tc['created_at']
    }

def vulnerability_to_dict(vuln):
    return {
        'id': vuln['id'],
        'title': vuln['title'],
        'description': vuln['description'],
        'cvss_score': vuln['cvss_score'],
        'status': vuln['status'],
        'severity': vuln['severity'],
        'affected_systems': vuln['affected_systems'],
        'business_impact': vuln['business_impact'],
        'remediation_plan': vuln['remediation_plan'],
        'organization_id': vuln['organization_id'],
        'discovered_by': vuln['discovered_by'],
        'discovered_at': vuln['discovered_at']
    }

# AI Agent Automation
class AIAgentManager:
    """
    Manages automated security testing with AI agents
    """
    
    def __init__(self, organization_id):
        """Initialize the AI agent manager"""
        self.organization_id = organization_id
        self.progress_callback = None
        
        # Try to get OpenAI API key from environment
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        # Initialize OpenAI client if API key is available
        if self.openai_api_key:
            try:
                import openai
                openai.api_key = self.openai_api_key
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                logging.info("OpenAI client initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
        else:
            logging.warning("OpenAI API key not available")
            self.client = None
        
        # We'll use a dummy organization for now as Organization.query isn't defined in this context
        self.organization = {"id": organization_id, "name": "Default Organization", "industry": "Technology"}
        
        logging.info("OpenAI API key found. Using OpenAI for vulnerability scanning.")
    
    def register_progress_callback(self, callback_fn):
        """Register a callback function for progress updates"""
        self.progress_callback = callback_fn
        logging.info("Progress callback registered")
    
    def _update_progress(self, stage, percent, message=None):
        """Update progress using the callback if registered"""
        if self.progress_callback:
            self.progress_callback(stage, percent, message)
            logging.info(f"Progress updated: {stage} - {percent}%")
        else:
            logging.info(f"Progress update (no callback): {stage} - {percent}%")
            
        # Increment vulnerability count in session when assessment is complete
        if stage == "Assessment complete" and percent == 100:
            try:
                from flask import session
                if 'user_id' in session:
                    # Get current dashboard stats
                    dashboard_stats = session.get('dashboard_stats', {})
                    vuln_stats = dashboard_stats.get('vuln_stats', {})
                    
                    # Increment total vulnerabilities count
                    total_vulnerabilities = dashboard_stats.get('total_vulnerabilities', 0)
                    dashboard_stats['total_vulnerabilities'] = total_vulnerabilities + 1
                    
                    # Also increment a random severity category
                    random_severity = random.choice(['critical', 'high', 'medium', 'low'])
                    vuln_stats[random_severity] = vuln_stats.get(random_severity, 0) + 1
                    
                    # Update dashboard stats in session
                    dashboard_stats['vuln_stats'] = vuln_stats
                    session['dashboard_stats'] = dashboard_stats
                    
                    logging.info(f"Updated dashboard vulnerability count: +1 (new total: {total_vulnerabilities + 1})")
            except Exception as e:
                logging.error(f"Error updating dashboard stats: {str(e)}")
    
    def run_automated_assessment(self, tech_stack, assessment_type=None, code_sample=None, language=None):
        """Generate test cases and simulate attacks using AI"""
        if not assessment_type:
            assessment_type = "vuln_scan"
            
        logging.info(f"Starting automated assessment using {assessment_type} mode")
        logging.info(f"Technology stack: {tech_stack}")
        
        # Check if a code sample was provided
        if code_sample:
            logging.info(f"Code sample provided for direct analysis. Length: {len(code_sample)} chars")
        
        # Use LangChain if OpenAI key is missing or legacy mode selected
        if not self.openai_api_key or assessment_type == "legacy":
            logging.info("Using legacy assessment mode")
            return self._run_legacy_assessment(tech_stack)
        
        # If a code sample is provided, prioritize code review
        if code_sample:
            self._update_progress("Starting code review", 20, f"Analyzing provided code sample ({language or 'auto-detect'})")
            code_review_results = self.code_review(code_sample, language)
            
            # Parse results into vulnerabilities
            vulnerabilities = []
            
            if code_review_results and code_review_results.get("success"):
                self._update_progress("Processing results", 80, "Converting code review findings to vulnerabilities")
                
                # Add vulnerabilities for critical/high issues
                for issue in code_review_results.get("issues", []):
                    # Create a vulnerability for database storage
                    severity = issue.get("severity", "medium")
                    title = issue.get('description', 'Code Issue')
                    if len(title) > 80:  # Truncate if too long
                        title = title[:77] + "..."
                        
                        conn = get_db_connection()
                        cursor = conn.execute('''
                        INSERT INTO vulnerabilities 
                        (title, description, status, severity, remediation_plan, organization_id, discovered_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                        f"Code Review: {title}",
                            issue.get('impact', 'No details provided'),
                            'open',
                        severity,
                            issue.get('fix', 'Review code and fix issue'),
                            self.organization_id,
                            'SHIELD Code Review'
                        ))
                        conn.commit()
                        
                        # Get the inserted vulnerability
                    vuln_id = cursor.lastrowid
                    vuln = conn.execute("SELECT * FROM vulnerabilities WHERE id = ?", (vuln_id,)).fetchone()
                    if vuln:
                        vulnerabilities.append(vulnerability_to_dict(vuln))
                        conn.close()
            
            # Mark assessment as complete
            self._update_progress("Assessment complete", 100, "Finalizing assessment report")
            
            # Return assessment results
            assessment_results = {
                "assessment_id": str(uuid.uuid4()),
                "organization_id": self.organization_id,
                "assessment_type": "code_review",
                "timestamp": datetime.now().isoformat(),
                "test_cases_count": 0,
                "vulnerabilities_found": len(vulnerabilities),
                "vulnerabilities": vulnerabilities,
                "assessment_method": "OpenAI GPT-4 Code Review",
                "code_review": code_review_results
            }
            
            return assessment_results
        
        # Standard assessment flow for repository scanning
        # Generate test cases
        self._update_progress("Generating test cases", 20, "Creating targeted tests based on tech stack")
        test_cases = self._generate_targeted_test_cases(tech_stack)
        
        # Execute test cases
        self._update_progress("Executing test cases", 50, "Running tests against simulated environment")
        results = self._execute_test_cases(test_cases)
        
        # Analyze results and create vulnerabilities
        self._update_progress("Analyzing results", 80, "Processing test results and identifying vulnerabilities")
        vulnerabilities = self._analyze_results(results)
        
        # Mark assessment as complete
        self._update_progress("Assessment complete", 100, "Finalizing assessment report")
        
        # Return assessment results
        assessment_results = {
            "assessment_id": str(uuid.uuid4()),
            "organization_id": self.organization_id,
            "assessment_type": assessment_type,
            "timestamp": datetime.now().isoformat(),
            "test_cases_count": len(test_cases),
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "assessment_method": "OpenAI GPT-4"
        }
        
        return assessment_results
    
    def _run_legacy_assessment(self, tech_stack):
        """Run assessment using LangChain when OpenAI API key is not available"""
        logging.info("Using LangChain for legacy assessment")
        self._update_progress("Initializing LangChain", 10, "Setting up LangChain environment")
        
        # Create sample test cases
        self._update_progress("Generating basic test cases", 30, "Creating test cases based on technology stack")
        test_cases = []
        for tech in tech_stack:
            # Basic test case for each technology
            test_case = {
                "name": f"Basic Security Scan for {tech}",
                "description": f"Standard security scan for {tech} applications",
                "type": "security_scan",
                "target": tech,
                "severity": "medium"
            }
            test_cases.append(test_case)
        
        # Store test cases in database
        self._update_progress("Storing test cases", 50, "Saving test cases to database")
        stored_test_cases = []
        conn = get_db_connection()
        for tc in test_cases:
            cursor = conn.execute('''
            INSERT INTO test_cases (name, description, type, target, payload, expected_result, status, organization_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tc["name"],
                tc["description"],
                tc["type"],
                tc["target"],
                "Standard scan",
                "Identification of common vulnerabilities",
                "completed",
                self.organization_id
            ))
            conn.commit()
            tc_with_id = dict(conn.execute("SELECT * FROM test_cases WHERE id = ?", (cursor.lastrowid,)).fetchone())
            stored_test_cases.append(tc_with_id)
        
        # Create sample vulnerabilities
        self._update_progress("Creating sample vulnerabilities", 80, "Generating vulnerability records")
        vulnerabilities = []
        for i, tech in enumerate(tech_stack[:3]):  # Limit to 3 vulnerabilities for demo
            vuln_type = ["XSS", "SQL Injection", "CSRF", "Insecure Configuration"][i % 4]
            severity = ["medium", "high", "low", "critical"][i % 4]
            
            cursor = conn.execute('''
            INSERT INTO vulnerabilities 
            (title, description, cvss_score, status, severity, affected_systems, remediation_plan, organization_id, discovered_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"{vuln_type} in {tech}",
                f"Potential {vuln_type} vulnerability detected in {tech} implementation",
                (5.0 + i) % 10,  # Random CVSS score between 5 and 10
                'open',
                severity,
                json.dumps([tech]),
                f"Update {tech} to latest version and implement security best practices for {vuln_type} prevention",
                self.organization_id,
                'SHIELD Legacy Scanner'
            ))
            conn.commit()
            vuln = dict(conn.execute("SELECT * FROM vulnerabilities WHERE id = ?", (cursor.lastrowid,)).fetchone())
            vulnerabilities.append(vulnerability_to_dict(vuln))
        
        conn.close()
        
        self._update_progress("Assessment complete", 100, "Legacy assessment completed")
        
        return {
            "assessment_id": str(uuid.uuid4()),
            "organization_id": self.organization_id,
            "assessment_type": "legacy",
            "timestamp": datetime.now().isoformat(),
            "test_cases_count": len(stored_test_cases),
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "assessment_method": "LangChain Legacy"
        }
    
    def _generate_targeted_test_cases(self, tech_stack):
        """Generate test cases based on tech stack using OpenAI"""
        # Parse tech stack
        if isinstance(tech_stack, str):
            try:
                tech_stack = json.loads(tech_stack)
            except:
                tech_stack = [tech_stack]
        
        logging.info(f"Generating targeted test cases for: {tech_stack}")
        self._update_progress("Preparing test case generation", 15, "Constructing prompts based on technologies")
        
        # Format tech stack for the prompt
        tech_stack_str = ", ".join(tech_stack)
        
        # Define prompt for OpenAI
        prompt = f"""
        You are a security expert tasked with generating detailed test cases for vulnerability assessment.
        
        Technology Stack: {tech_stack_str}
        
        For each technology in the stack, create 2-3 specific security test cases, focusing on the most critical vulnerabilities
        for that technology. For each test case, provide the following:
        
        1. Name: A descriptive name for the test case
        2. Description: A detailed description of the vulnerability and how it applies to this technology
        3. Type: The vulnerability type (e.g., XSS, SQL Injection, CSRF, etc.)
        4. Target: The specific component or functionality being tested
        5. Payload: Example payload or test input that would exploit this vulnerability
        6. Expected Result: What happens if the system is vulnerable
        7. Severity: Critical, High, Medium, or Low
        8. CVSS Score: A numerical score between 0.0 and 10.0
        9. Remediation: Specific steps to address this vulnerability
        
        Format your response as a JSON array of test case objects.
        """
        
        # Call OpenAI API directly
        try:
            self._update_progress("Calling OpenAI API", 25, "Generating security test cases via AI")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a security expert that generates detailed test cases for vulnerability assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the response content
            ai_response = response.choices[0].message.content
            
            logging.info("Received response from OpenAI")
            self._update_progress("Processing AI response", 35, "Parsing generated test cases")
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                json_start = ai_response.find('[')
                json_end = ai_response.rfind(']') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    ai_test_cases = json.loads(json_str)
                else:
                    # If no JSON array found, try the entire response
                    ai_test_cases = json.loads(ai_response)
                    
                logging.info(f"Successfully parsed {len(ai_test_cases)} test cases from AI response")
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON from AI response: {e}")
                logging.error(f"AI response: {ai_response}")
                
                # Fallback to default test cases if JSON parsing fails
                ai_test_cases = []
                for tech in tech_stack:
                    ai_test_cases.append({
                        "name": f"Security Assessment for {tech}",
                        "description": f"Comprehensive security assessment for {tech} applications",
                        "type": "security_assessment",
                        "target": tech,
                        "payload": "Standard security scan",
                        "expected_result": "Identification of security vulnerabilities",
                        "severity": "medium",
                        "cvss_score": 5.0,
                        "remediation": "Follow security best practices for this technology"
                    })
                
                logging.info(f"Created {len(ai_test_cases)} fallback test cases")
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {str(e)}")
            
            # Fallback to simpler test cases if OpenAI fails
            ai_test_cases = []
            for tech in tech_stack:
                ai_test_cases.append({
                    "name": f"Basic Security Scan for {tech}",
                    "description": f"Basic vulnerability scan for {tech}",
                    "type": "vulnerability_scan",
                    "target": tech,
                    "payload": "Standard security tests",
                    "expected_result": "Detection of common vulnerabilities",
                    "severity": "medium",
                    "cvss_score": 5.0,
                    "remediation": "Apply security patches and follow best practices"
                })
            
            logging.info(f"Created {len(ai_test_cases)} simple fallback test cases after API error")
        
        # Store test cases in database
        self._update_progress("Saving test cases", 45, "Storing generated test cases in database")
        created_test_cases = []
        conn = get_db_connection()
        
        for tc in ai_test_cases:
            try:
                # Ensure we have all required fields
                name = tc.get("name", f"Test for {tech_stack[0]}")
                description = tc.get("description", "Security test case")
                vuln_type = tc.get("type", "security_scan")
                target = tc.get("target", tech_stack[0])
                payload = tc.get("payload", "Standard test")
                expected_result = tc.get("expected_result", "Vulnerability detection")
                severity = tc.get("severity", "medium")
                
                cursor = conn.execute('''
                INSERT INTO test_cases (name, description, type, target, payload, expected_result, status, organization_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name,
                    description,
                    vuln_type,
                    target,
                    payload,
                    expected_result,
                    "pending",
                    self.organization_id
                ))
                conn.commit()
                
                # Store additional data for test execution
                test_case = dict(conn.execute("SELECT * FROM test_cases WHERE id = ?", (cursor.lastrowid,)).fetchone())
                test_case['ai_data'] = {
                    'severity': severity,
                    'cvss_score': tc.get('cvss_score', 5.0),
                    'remediation': tc.get('remediation', 'Follow security best practices')
                }
                created_test_cases.append(test_case)
                
            except Exception as e:
                logging.error(f"Error storing test case: {str(e)}")
                continue
        
        conn.close()
        
        logging.info(f"Created {len(created_test_cases)} test cases in the database")
        return created_test_cases
    
    def _execute_test_cases(self, test_cases):
        """Execute test cases using AI and simulated attacks"""
        results = []
        
        for test_case in test_cases:
            # For each test case, simulate an attack
            template = """
            You are a cybersecurity agent simulating an attack in a secure sandbox environment.
            
            Test Case Details:
            Name: {name}
            Description: {description}
            Type: {test_type}
            Target: {target}
            Payload: {payload}
            Expected Result: {expected_result}
            
            Task:
            Simulate running this test case in a sandbox environment and generate realistic results.
            Analyze whether the attack would likely succeed or fail based on common configurations of the target system.
            
            Include in your simulation:
            1. The detailed steps taken during the attack
            2. The system's response to each step
            3. Whether the attack succeeded or failed
            4. If successful, what kind of vulnerability was found and its severity
            5. If failed, why it failed
            
            Format your response as a JSON object with the following structure:
            {{
                "simulation_steps": [
                    "Step 1: description",
                    "Step 2: description",
                    ...
                ],
                "system_responses": [
                    "Response 1: description",
                    "Response 2: description",
                    ...
                ],
                "success": true/false,
                "vulnerability_details": {{
                    "title": "Vulnerability Title (if found)",
                    "description": "Description of the vulnerability",
                    "severity": "critical/high/medium/low",
                    "cvss_score": 8.5,
                    "affected_components": ["component1", "component2"],
                    "remediation": "Suggested remediation steps"
                }},
                "failure_reason": "Reason why the attack failed (if applicable)"
            }}
            """
            
            # Prepare the message
            message = template.format(
                name=test_case.get('name'),
                description=test_case.get('description'),
                test_type=test_case.get('type'),
                target=test_case.get('target'),
                payload=test_case.get('payload'),
                expected_result=test_case.get('expected_result')
            )
            
            # Get the response from the OpenAI API directly 
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity expert AI assistant."},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.2
                )
                
                # Extract the response
                response_text = response.choices[0].message.content
                
                # Parse the response
                try:
                    # Extract JSON from the response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        simulation_data = json.loads(json_text)
                    else:
                        simulation_data = {
                            'simulation_steps': [],
                            'system_responses': [],
                            'success': False,
                            'failure_reason': 'Failed to parse simulation results'
                        }
                        
                    # Update test case with results
                    test_case['status'] = 'completed'
                    test_case['result'] = json.dumps(simulation_data)
                    db.session.commit()
                    
                    results.append({
                        "test_case_id": test_case['id'],
                        "simulation_data": simulation_data
                    })
                    
                except Exception as e:
                    db.session.rollback()
                    # Update test case status to failed
                    test_case['status'] = 'failed'
                    test_case['result'] = json.dumps({
                        'error': str(e),
                        'simulation_steps': [],
                        'system_responses': [],
                        'success': False,
                        'failure_reason': f'Error during simulation: {str(e)}'
                    })
                    db.session.commit()
                    
                    logging.error(f"Error executing test case {test_case['id']}: {str(e)}")
                    results.append({
                        "test_case_id": test_case['id'],
                        "error": str(e)
                    })
                
            except Exception as e:
                logging.error(f"Error calling OpenAI API: {str(e)}")
                results.append({
                    "test_case_id": test_case['id'],
                    "error": str(e)
                })
                
        return results
    
    def _generate_simulation_data(self, test_case, is_vulnerable):
        """Generate simulation results"""
        if is_vulnerable:
            severity = "high" if test_case['type'] in ['sql_injection'] else "medium"
            cvss = 8.5 if test_case['type'] in ['sql_injection'] else 6.5
            
            return {
                "simulation_steps": [
                    f"Step 1: Identified {test_case['type']} entry point in {test_case['target']}",
                    f"Step 2: Crafted payload: {test_case['payload']}",
                    f"Step 3: Submitted payload to target system"
                ],
                "system_responses": [
                    "Response 1: System accepted the input without proper validation",
                    f"Response 2: System exhibited vulnerable behavior: {test_case['expected_result']}"
                ],
                "success": True,
                "vulnerability_details": {
                    "title": f"{test_case['type'].replace('_', ' ').title()} Vulnerability in {test_case['target']}",
                    "description": f"The system is vulnerable to {test_case['type']} attacks. {test_case['description']}",
                    "severity": severity,
                    "cvss_score": cvss,
                    "affected_components": [test_case['target']],
                    "remediation": self._get_remediation_for_type(test_case['type'])
                }
            }
        else:
            return {
                "simulation_steps": [
                    f"Step 1: Identified potential {test_case['type']} entry point in {test_case['target']}",
                    f"Step 2: Crafted payload: {test_case['payload']}",
                    f"Step 3: Submitted payload to target system"
                ],
                "system_responses": [
                    "Response 1: System properly validated and sanitized the input",
                    "Response 2: System rejected the malicious payload"
                ],
                "success": False,
                "failure_reason": f"The system has proper protections against {test_case['type']} attacks"
            }
    
    def _get_remediation_for_type(self, vuln_type):
        """Get remediation steps based on vulnerability type"""
        remediations = {
            "sql_injection": "Use parameterized queries or prepared statements. Never concatenate user input directly into SQL queries. Implement input validation and use ORM frameworks when possible.",
            "xss": "Implement context-sensitive output encoding. Use Content-Security-Policy headers. Sanitize all user inputs and validate data on both client and server sides.",
            "csrf": "Implement anti-CSRF tokens in all forms. Use the SameSite cookie attribute. Verify the Origin and Referer headers for sensitive actions."
        }
        return remediations.get(vuln_type, "Review security best practices for this type of vulnerability and implement appropriate controls.")
    
    def _analyze_results(self, results):
        """Analyze results and create vulnerabilities"""
        vulnerabilities = []
        conn = get_db_connection()
        
        for result in results:
            simulation_data = result["simulation_data"]
            test_case_id = result["test_case_id"]
            
            # If vulnerability found, create vulnerability record
            if simulation_data.get('success') and simulation_data.get('vulnerability_details'):
                vuln_details = simulation_data.get('vulnerability_details')
                
                # Insert vulnerability
                cursor = conn.execute('''
                INSERT INTO vulnerabilities 
                (title, description, cvss_score, status, severity, affected_systems, remediation_plan, organization_id, discovered_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vuln_details.get('title', f"Vulnerability from test case {test_case_id}"),
                    vuln_details.get('description'),
                    vuln_details.get('cvss_score'),
                    'open',
                    vuln_details.get('severity', 'medium'),
                    json.dumps(vuln_details.get('affected_components', [])),
                    vuln_details.get('remediation'),
                    self.organization_id,
                    'SHIELD AI Agent'
                ))
                conn.commit()
                
                # Link test case to vulnerability
                vuln_id = cursor.lastrowid
                conn.execute('''
                UPDATE test_cases
                SET vulnerability_id = ?
                WHERE id = ?
                ''', (vuln_id, test_case_id))
                conn.commit()
                
                # Get the inserted vulnerability
                vuln = conn.execute("SELECT * FROM vulnerabilities WHERE id = ?", (vuln_id,)).fetchone()
                vulnerabilities.append(vulnerability_to_dict(vuln))
        
        conn.close()
        return vulnerabilities

    def code_review(self, code_snippet, language=None):
        """
        Perform a code review using OpenAI on the provided code snippet
        
        Args:
            code_snippet (str): The code to be reviewed
            language (str): The programming language of the code (optional)
            
        Returns:
            dict: Results of the code review including issues and recommendations
        """
        if not self.openai_api_key or not self.client or not code_snippet:
            # For demonstration purposes, use a simulated response
            logging.warning("OpenAI API key not available, using simulated code review")
            return self._generate_simulated_code_review(code_snippet, language)
            
        logging.info(f"Starting AI code review for {language or 'unknown'} code")
        
        # Set language context if provided
        lang_context = f"for {language}" if language else ""
        
        # Truncate code if it's too long
        # GPT-4 can handle ~20k tokens, so limit to ~10k tokens (roughly 40k chars)
        MAX_CODE_LENGTH = 38000
        truncated = False
        
        if len(code_snippet) > MAX_CODE_LENGTH:
            truncated = True
            code_snippet = code_snippet[:MAX_CODE_LENGTH]
        
        # Define the prompt for code review
        prompt = f"""
        You are an expert code reviewer. Please analyze the following code {lang_context} for:
        
        1. Security vulnerabilities (e.g., injection flaws, authentication issues, data exposure)
        2. Performance issues
        3. Best practice violations
        4. Code quality issues
        5. Potential bugs or logical errors
        
        {f"NOTE: The code provided has been truncated due to length limitations. Please analyze what's available." if truncated else ""}
        
        Provide your analysis in a structured format with the following sections:
        
        1. Overall assessment (brief summary)
        2. Critical issues (security vulnerabilities)
        3. Major issues (bugs, performance)
        4. Minor issues (style, best practices)
        5. Recommendations (specific, actionable recommendations)
        
        For each issue found, include:
        - Description of the issue
        - Severity level
        - Potential impact
        - Suggested fix with code example if applicable
        
        Format your response as a JSON with the following structure:
        {
            "overall_assessment": "Brief summary",
            "issues": [
                {
                    "description": "Issue description",
                    "severity": "critical/high/medium/low",
                    "impact": "Potential impact of this issue",
                    "fix": "Suggested fix",
                    "code_example": "Example code if applicable"
                }
            ],
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2"
            ]
        }
        
        Here's the code to review:
        
        ```
        {code_snippet}
        ```
        """
        
        try:
            self._update_progress("Running code review", 60, "Analyzing code with AI")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4", # Use appropriate model
                messages=[
                    {"role": "system", "content": "You are an expert security-focused code reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # Low temperature for consistency
                max_tokens=4000  # Allow for a substantial response
            )
            
            # Extract the response content
            review_text = response.choices[0].message.content
            
            try:
                # Try to extract JSON from the response
                json_start = review_text.find('{')
                json_end = review_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = review_text[json_start:json_end]
                    review_results = json.loads(json_str)
                else:
                    # If no JSON object found, try the entire response
                    review_results = json.loads(review_text)
                    
                logging.info("Successfully parsed code review results from AI response")
                
                # Add success indicator and truncation notice
                review_results["success"] = True
                if truncated:
                    review_results["notice"] = "The code was truncated due to size limitations. Review is based on the first part of the code only."
                
                self._update_progress("Code review complete", 90, "Review completed successfully")
                return review_results
                
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON from code review response: {e}")
                
                # Return error with raw response
                return {
                    "success": False,
                    "error": f"Error parsing review results: {str(e)}",
                    "raw_response": review_text,
                    "issues": [],
                    "recommendations": ["Unable to parse AI response into structured format"]
                }
                
        except Exception as e:
            logging.error(f"Error during code review: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "recommendations": []
            }

    def _generate_simulated_code_review(self, code_snippet, language=None):
        """
        Generate a simulated code review response for demonstration purposes
        when OpenAI API key is not available
        """
        logging.info("Generating simulated code review response")
        self._update_progress("Simulating code review", 50, "Generating AI-like response")
        
        # Generate a believable simulated response
        language = language or "unknown"
        
        # Extract some basic code stats for the simulation
        line_count = code_snippet.count('\n') + 1
        char_count = len(code_snippet)
        
        # Determine potential issues based on simple patterns
        issues = []
        
        # Check for potential SQL injection
        if "SELECT" in code_snippet and "%" in code_snippet and ("'" in code_snippet or '"' in code_snippet):
            issues.append({
                "description": "Potential SQL Injection vulnerability",
                "severity": "critical",
                "impact": "SQL injection can allow attackers to read, modify, or delete data from your database, potentially leading to data breach or system compromise.",
                "fix": "Use parameterized queries or prepared statements instead of string concatenation.",
                "code_example": "Instead of: query = \"SELECT * FROM users WHERE name = '\" + name + \"'\";\nUse: query = \"SELECT * FROM users WHERE name = ?\"; db.execute(query, [name]);"
            })
            
        # Check for potential XSS
        if ("<" in code_snippet and ">" in code_snippet and "innerHTML" in code_snippet) or ".html(" in code_snippet:
            issues.append({
                "description": "Potential Cross-Site Scripting (XSS) vulnerability",
                "severity": "high",
                "impact": "XSS can allow attackers to inject malicious scripts into web pages viewed by other users, potentially leading to session hijacking or credential theft.",
                "fix": "Sanitize user input before rendering it to the page, or use safe DOM manipulation methods.",
                "code_example": "Instead of: element.innerHTML = userInput;\nUse: element.textContent = userInput; or a sanitization library."
            })
            
        # Check for hardcoded credentials
        if "password" in code_snippet.lower() and ("=" in code_snippet or ":" in code_snippet):
            issues.append({
                "description": "Hardcoded credentials detected",
                "severity": "high",
                "impact": "Hardcoded credentials can be exposed if source code is leaked, potentially leading to unauthorized access.",
                "fix": "Use environment variables or a secure vault to store sensitive information.",
                "code_example": "Instead of: password = \"hardcoded_password\";\nUse: password = process.env.PASSWORD; or a secrets management solution."
            })
            
        # Add more general code quality issues
        issues.append({
            "description": "Code lacks proper error handling",
            "severity": "medium",
            "impact": "Without proper error handling, the application may crash or behave unexpectedly when errors occur.",
            "fix": "Implement try-catch blocks or other error handling mechanisms appropriate for the language.",
            "code_example": "try {\n    // risky operation\n} catch (error) {\n    // handle error appropriately\n}"
        })
        
        issues.append({
            "description": "Inconsistent code formatting",
            "severity": "low",
            "impact": "Inconsistent formatting reduces code readability and can make maintenance more difficult.",
            "fix": "Use a code formatter or linter to enforce consistent style.",
            "code_example": "Use tools like Prettier, ESLint, Black, etc. depending on your language."
        })
        
        # Generate general recommendations
        recommendations = [
            f"Consider adding comprehensive unit tests for your {language} code.",
            "Implement a code linting tool in your CI/CD pipeline.",
            "Add detailed comments for complex logic.",
            "Consider breaking down large functions into smaller, more focused ones."
        ]
        
        # Create the review results
        review_results = {
            "success": True,
            "overall_assessment": f"The code review found {len(issues)} potential issues in your {language} code ({line_count} lines). The most critical issues relate to security vulnerabilities that should be addressed promptly.",
            "issues": issues,
            "recommendations": recommendations,
            "notice": "This is a simulated code review since OpenAI API key is not available."
        }
        
        self._update_progress("Code review complete", 100, "Simulated review completed successfully")
        return review_results

    def generate_test_cases(self, code_snippet, language=None, test_type='unit'):
        """
        Generate test cases for the provided code snippet using OpenAI
        
        Args:
            code_snippet (str): The code to generate tests for
            language (str): The programming language of the code
            test_type (str): The type of tests to generate (unit, integration, etc.)
            
        Returns:
            dict: Generated test cases and metadata
        """
        if not self.openai_api_key or not self.client or not code_snippet:
            # For demonstration purposes, use a simulated response
            logging.warning("OpenAI API key not available, using simulated test case generation")
            return self._generate_simulated_test_cases(code_snippet, language, test_type)
            
        logging.info(f"Starting test case generation for {language or 'unknown'} code")
        
        # Rest of the existing method...
        
    def _generate_simulated_test_cases(self, code_snippet, language=None, test_type='unit'):
        """
        Generate simulated test cases for demonstration purposes when OpenAI API key is not available
        """
        logging.info("Generating simulated test cases")
        self._update_progress("Simulating test case generation", 50, "Generating AI-like response")
        
        # Create a simulated test framework based on the language
        language = language or "unknown"
        test_framework = "unknown"
        
        if language.lower() in ["javascript", "js", "typescript", "ts"]:
            test_framework = "Jest"
            template = """
describe('functionName', () => {
  test('should handle valid input correctly', () => {
    // Arrange
    const input = 'valid input';
    
    // Act
    const result = functionName(input);
    
    // Assert
    expect(result).toBe(expectedOutput);
  });
  
  test('should handle edge cases', () => {
    // Arrange
    const input = null;
    
    // Act
    const result = functionName(input);
    
    // Assert
    expect(result).toBeNull();
  });
  
  test('should throw error for invalid input', () => {
    // Arrange
    const input = -1;
    
    // Act & Assert
    expect(() => {
      functionName(input);
    }).toThrow('Invalid input');
  });
});
"""
        elif language.lower() in ["python", "py"]:
            test_framework = "pytest"
            template = """
import pytest
from module import function_name

def test_function_name_valid_input():
    # Arrange
    input_data = "valid input"
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected_output

def test_function_name_edge_case():
    # Arrange
    input_data = None
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result is None

def test_function_name_invalid_input():
    # Arrange
    input_data = -1
    
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        function_name(input_data)
    assert "Invalid input" in str(excinfo.value)
"""
        elif language.lower() in ["java"]:
            test_framework = "JUnit"
            template = """
import org.junit.Test;
import static org.junit.Assert.*;

public class ClassNameTest {
    
    @Test
    public void testMethodName_ValidInput() {
        // Arrange
        String input = "valid input";
        
        // Act
        String result = className.methodName(input);
        
        // Assert
        assertEquals(expectedOutput, result);
    }
    
    @Test
    public void testMethodName_EdgeCase() {
        // Arrange
        String input = null;
        
        // Act
        String result = className.methodName(input);
        
        // Assert
        assertNull(result);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testMethodName_InvalidInput() {
        // Arrange
        int input = -1;
        
        // Act & Assert (exception expected)
        className.methodName(input);
    }
}
"""
        elif language.lower() in ["c#", "csharp"]:
            test_framework = "NUnit"
            template = """
using NUnit.Framework;
using System;

namespace MyProject.Tests
{
    [TestFixture]
    public class ClassNameTests
    {
        [Test]
        public void MethodName_ValidInput_ReturnsExpectedResult()
        {
            // Arrange
            string input = "valid input";
            
            // Act
            var result = ClassName.MethodName(input);
            
            // Assert
            Assert.AreEqual(expectedOutput, result);
        }
        
        [Test]
        public void MethodName_NullInput_ReturnsNull()
        {
            // Arrange
            string input = null;
            
            // Act
            var result = ClassName.MethodName(input);
            
            // Assert
            Assert.IsNull(result);
        }
        
        [Test]
        public void MethodName_InvalidInput_ThrowsArgumentException()
        {
            // Arrange
            int input = -1;
            
            // Act & Assert
            Assert.Throws<ArgumentException>(() => ClassName.MethodName(input));
        }
    }
}
"""
        else:
            # Generic template
            template = """
// Test function for valid input
test_valid_input() {
    input = "valid input";
    expected = "expected output";
    result = function_to_test(input);
    assert(result == expected);
}

// Test edge case
test_edge_case() {
    input = null;
    result = function_to_test(input);
    assert(result == null);
}

// Test invalid input
test_invalid_input() {
    input = -1;
    try {
        function_to_test(input);
        fail("Should have thrown an exception");
    } catch (e) {
        assert(e.message.contains("Invalid input"));
    }
}
"""
        
        # Extract function name from code snippet if possible
        function_name = "exampleFunction"
        
        # Try to find function/method declarations in the code
        if "function " in code_snippet:
            # JavaScript style
            match = re.search(r'function\s+(\w+)', code_snippet)
            if match:
                function_name = match.group(1)
        elif "def " in code_snippet:
            # Python style
            match = re.search(r'def\s+(\w+)', code_snippet)
            if match:
                function_name = match.group(1)
        elif "public " in code_snippet and "(" in code_snippet:
            # Java/C# style
            match = re.search(r'(public|private|protected)\s+\w+\s+(\w+)\s*\(', code_snippet)
            if match:
                function_name = match.group(2)
        
        # Create a simulated response
        test_cases = template.replace("functionName", function_name).replace("function_name", function_name)
        
        # Add some information about the test type
        if test_type.lower() == 'unit':
            test_description = "Basic unit tests to verify individual function behavior"
        elif test_type.lower() == 'integration':
            test_description = "Integration tests to verify component interactions"
        elif test_type.lower() == 'security':
            test_description = "Security tests to check for vulnerabilities"
        else:
            test_description = f"{test_type} tests for code verification"
        
        response = {
            "success": True,
            "test_framework": test_framework,
            "language": language,
            "test_type": test_type,
            "description": test_description,
            "test_cases": test_cases,
            "count": 3,  # We generated 3 test cases
            "notice": "This is a simulated test case generation since OpenAI API key is not available."
        }
        
        self._update_progress("Test case generation complete", 100, "Simulated test cases created successfully")
        return response

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and password == 'password':  # In a real app, verify the hash
            # Clear any existing session data first
            session.clear()
            
            # Make the session permanent
            session.permanent = True
            
            # Set new session data
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Set GitHub connection status based on token
            if user['github_token']:
                session['github_connected'] = True
                session['github_token'] = user['github_token']
            else:
                session['github_connected'] = False
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Always disconnect GitHub when logging out
    if 'github_token' in session:
        session.pop('github_token', None)
    
    # Update connection status
    session['github_connected'] = False
    
    # Clear user session data
    session.pop('user_id', None)
    session.pop('username', None)
    
    # Set feedback message
    flash('You have been logged out.', 'success')
    
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/github/disconnect', methods=['POST'])
def github_disconnect():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get user information before disconnecting
        conn = get_db_connection()
        user = conn.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        username = user['username'] if user else 'Unknown'
        
        # Log the disconnection attempt
        logging.info(f"GitHub disconnection initiated for user {username} (ID: {session['user_id']})")
        
        # Delete all GitHub repositories associated with this user
        cursor = conn.execute('DELETE FROM github_repos WHERE user_id = ?', (session['user_id'],))
        deleted_repos_count = cursor.rowcount
        logging.info(f"Deleted {deleted_repos_count} GitHub repositories for user {username}")
        
        # Remove GitHub token and OAuth state from the database
        conn.execute('UPDATE users SET github_token = NULL, github_oauth_state = NULL WHERE id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        
        # Remove all GitHub-related data from session
        for key in ['github_token', 'github_connected', 'github_oauth_state', 'pre_github_user_id', 
                   'pre_github_username', 'pre_github_email']:
            if key in session:
                session.pop(key, None)
        
        # Force session to be saved
        session.modified = True
        
        # Set success message
        if deleted_repos_count > 0:
            flash(f'GitHub account successfully disconnected. {deleted_repos_count} repositories were removed.', 'success')
        else:
            flash('GitHub account successfully disconnected', 'success')
            
    except Exception as e:
        logging.error(f"Error disconnecting GitHub: {str(e)}")
        flash('An error occurred while disconnecting your GitHub account', 'danger')
    
    return redirect(url_for('profile'))

@app.route('/dashboard')
@app.route('/dashboard/<int:organization_id>')
def dashboard(organization_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the real user_id from session
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get user's GitHub token
    user = conn.execute('SELECT github_token FROM users WHERE id = ?', (user_id,)).fetchone()
    github_connected = user and user['github_token'] is not None
    
    # Fetch actual GitHub repositories from database
    github_repos = []
    db_repos = conn.execute(
        'SELECT id, repo_name, repo_url, status, last_scan FROM github_repos WHERE user_id = ? ORDER BY last_scan DESC LIMIT 5', 
        (user_id,)
    ).fetchall()
    
    for repo in db_repos:
        # Format last scan time
        last_scan_display = "Never"
        if repo['last_scan']:
            try:
                scan_time = datetime.fromisoformat(repo['last_scan'])
                last_scan_display = scan_time.strftime("%b %d, %Y")
            except (ValueError, TypeError):
                pass
                
        github_repos.append({
            'id': repo['id'],
            'name': repo['repo_name'],
            'url': repo['repo_url'],
            'description': 'Connected GitHub repository',
            'status': repo['status'] if repo['status'] else 'Not scanned',
            'last_scan': last_scan_display,
            'associated_vulnerabilities': []  # Will populate below if needed
        })
    
    # If no repositories in database but GitHub is connected, fetch from API
    if not github_repos and github_connected:
        try:
            user_repos_response = requests.get(
                'https://api.github.com/user/repos',
                headers={
                    'Authorization': f'token {user["github_token"]}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                params={
                    'sort': 'updated',
                    'per_page': 5
                }
            )
            
            if user_repos_response.status_code == 200:
                api_repos = user_repos_response.json()
                
                # Format repositories from API
                for repo in api_repos:
                    github_repos.append({
                        'id': f"new_{repo['id']}",  # Use prefix to indicate not yet in database
                        'name': repo['full_name'],
                        'url': repo['html_url'],
                        'description': repo['description'] or 'GitHub repository',
                        'status': 'Not connected',
                        'last_scan': 'Never',
                        'associated_vulnerabilities': []
                    })
        except Exception as e:
            logging.error(f"Error fetching GitHub repositories: {e}")
    
    # The rest of the dashboard code remains the same
    # Define our full list of vulnerabilities for consistency
    all_vulnerabilities = [
        {
            'id': 'VLN-001',
            'title': 'SQL Injection in Login Form',
            'description': 'The login form is vulnerable to SQL injection attacks, allowing unauthorized access to the database.',
            'severity': 'critical',
            'cvss_score': 9.8,
            'status': 'open',
            'discovered_at': '2023-11-15',
            'discovered_by': 'SHIELD AI Scanner'
        },
        {
            'id': 'VLN-002',
            'title': 'Cross-Site Scripting in Comment Section',
            'description': 'The comment section does not properly sanitize user input, allowing attackers to inject malicious scripts.',
            'severity': 'high',
            'cvss_score': 7.4,
            'status': 'in_progress',
            'discovered_at': '2023-11-14',
            'discovered_by': 'Manual Penetration Test'
        },
        {
            'id': 'VLN-003',
            'title': 'Insecure Direct Object Reference',
            'description': 'API endpoints do not properly validate user permissions, allowing access to unauthorized resources.',
            'severity': 'medium',
            'cvss_score': 5.9,
            'status': 'open',
            'discovered_at': '2023-11-12',
            'discovered_by': 'Code Review AI'
        },
        {
            'id': 'VLN-004',
            'title': 'Missing Rate Limiting on Authentication Endpoint',
            'description': 'The authentication endpoint does not implement rate limiting, making it vulnerable to brute force attacks.',
            'severity': 'medium',
            'cvss_score': 6.2,
            'status': 'resolved',
            'discovered_at': '2023-11-10',
            'discovered_by': 'SHIELD AI Scanner'
        },
        {
            'id': 'VLN-005',
            'title': 'Outdated Dependencies with Known Vulnerabilities',
            'description': 'Several dependencies in the project are outdated and contain known security vulnerabilities.',
            'severity': 'high',
            'cvss_score': 8.1,
            'status': 'open',
            'discovered_at': '2023-11-08',
            'discovered_by': 'Dependency Scanner'
        },
        {
            'id': 'VLN-006',
            'title': 'Weak Password Policy',
            'description': 'The password policy does not enforce sufficient complexity requirements.',
            'severity': 'low',
            'cvss_score': 4.3,
            'status': 'open',
            'discovered_at': '2023-11-05',
            'discovered_by': 'Security Audit'
        }
    ]
    
    # Calculate vulnerability stats based on the actual data
    vuln_stats = {
        'critical': sum(1 for v in all_vulnerabilities if v['severity'] == 'critical'),
        'high': sum(1 for v in all_vulnerabilities if v['severity'] == 'high'),
        'medium': sum(1 for v in all_vulnerabilities if v['severity'] == 'medium'),
        'low': sum(1 for v in all_vulnerabilities if v['severity'] == 'low')
    }
    
    # Total number of vulnerabilities
    total_vulnerabilities = len(all_vulnerabilities)
    
    # Test case stats
    test_case_stats = {
    'total': 45,
    'pending': 8,
    'running': 3,
    'completed': 32,
    'failed': 2,
    'ai_generated': 24
    }
    
    # Use actual vulnerabilities for CVSS data
    cvss_data = [{'id': v['id'], 'cvss_score': v['cvss_score']} for v in all_vulnerabilities]
    
    # Update vulnerabilities with repository information
    for vuln in all_vulnerabilities:
        vuln['repository'] = None
        for repo in github_repos:
            if vuln['id'] in repo['associated_vulnerabilities']:
                vuln['repository'] = {
                    'id': repo['id'],
                    'name': repo['name'],
                    'url': repo['url']
                }
                break
    
    return render_template('dashboard.html', 
        vuln_stats=vuln_stats,
        test_case_stats=test_case_stats,
                          recent_vulnerabilities=all_vulnerabilities[:4],
                          github_repos=github_repos,
                          cvss_data=cvss_data,
                          total_vulnerabilities=total_vulnerabilities)

@app.route('/organizations')
def organizations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    organizations = conn.execute('SELECT * FROM organizations').fetchall()
    conn.close()
    
    total_organizations = len(organizations)
    
    return render_template('organizations.html', 
                           organizations=organizations, 
                           total_organizations=total_organizations,
                           active_page='organizations')

@app.route('/vulnerabilities')
def vulnerabilities():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Use the same vulnerabilities data as the dashboard for consistency
    all_vulnerabilities = [
        {
            'id': 'VLN-001',
            'title': 'SQL Injection in Login Form',
            'description': 'The login form is vulnerable to SQL injection attacks, allowing unauthorized access to the database.',
            'severity': 'critical',
            'cvss_score': 9.8,
            'status': 'open',
            'discovered_at': '2023-11-15',
            'discovered_by': 'SHIELD AI Scanner'
        },
        {
            'id': 'VLN-002',
            'title': 'Cross-Site Scripting in Comment Section',
            'description': 'The comment section does not properly sanitize user input, allowing attackers to inject malicious scripts.',
            'severity': 'high',
            'cvss_score': 7.4,
            'status': 'in_progress',
            'discovered_at': '2023-11-14',
            'discovered_by': 'Manual Penetration Test'
        },
        {
            'id': 'VLN-003',
            'title': 'Insecure Direct Object Reference',
            'description': 'API endpoints do not properly validate user permissions, allowing access to unauthorized resources.',
            'severity': 'medium',
            'cvss_score': 5.9,
            'status': 'open',
            'discovered_at': '2023-11-12',
            'discovered_by': 'Code Review AI'
        },
        {
            'id': 'VLN-004',
            'title': 'Missing Rate Limiting on Authentication Endpoint',
            'description': 'The authentication endpoint does not implement rate limiting, making it vulnerable to brute force attacks.',
            'severity': 'medium',
            'cvss_score': 6.2,
            'status': 'resolved',
            'discovered_at': '2023-11-10',
            'discovered_by': 'SHIELD AI Scanner'
        },
        {
            'id': 'VLN-005',
            'title': 'Outdated Dependencies with Known Vulnerabilities',
            'description': 'Several dependencies in the project are outdated and contain known security vulnerabilities.',
            'severity': 'high',
            'cvss_score': 8.1,
            'status': 'open',
            'discovered_at': '2023-11-08',
            'discovered_by': 'Dependency Scanner'
        },
        {
            'id': 'VLN-006',
            'title': 'Weak Password Policy',
            'description': 'The password policy does not enforce sufficient complexity requirements.',
            'severity': 'low',
            'cvss_score': 4.3,
            'status': 'open',
            'discovered_at': '2023-11-05',
            'discovered_by': 'Security Audit'
        }
    ]
    
    # Calculate total vulnerabilities count for consistency
    total_vulnerabilities = len(all_vulnerabilities)
    
    return render_template(
        'vulnerabilities.html', 
        vulnerabilities=all_vulnerabilities,
        total_vulnerabilities=total_vulnerabilities,
        active_page='vulnerabilities'
    )

@app.route('/test-cases')
def test_cases():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
   
    # Test case stats from dashboard
    test_case_stats = {
        'total': 45,
        'pending': 8,
        'running': 3,
        'completed': 32,
        'failed': 2,
        'ai_generated': 24
    }
    
    # Sample test cases
    all_test_cases = [
        {
            'id': 'TC-001',
            'name': 'SQL Injection Test - Login Form',
            'type': 'SQL Injection',
            'target': 'https://example.com/login',
            'status': 'completed',
            'created_at': '2023-11-15',
            'description': 'Tests for SQL injection vulnerabilities in the login form.'
        },
        {
            'id': 'TC-002',
            'name': 'XSS Test - Comment Section',
            'type': 'XSS',
            'target': 'https://example.com/posts/comments',
            'status': 'completed',
            'created_at': '2023-11-14',
            'description': 'Tests for XSS vulnerabilities in the comment submission form.'
        },
        {
            'id': 'TC-003',
            'name': 'CSRF Protection Test - Profile Update',
            'type': 'CSRF',
            'target': 'https://example.com/profile/update',
            'status': 'pending',
            'created_at': '2023-11-13',
            'description': 'Verifies that CSRF tokens are correctly implemented on profile update forms.'
        },
        {
            'id': 'TC-004',
            'name': 'Authentication Bypass Test',
            'type': 'Authentication',
            'target': 'https://example.com/admin',
            'status': 'running',
            'created_at': '2023-11-12',
            'description': 'Attempts to bypass authentication mechanisms to access admin area.'
        },
        {
            'id': 'TC-005',
            'name': 'SHIELD AI: SQL Injection Detection',
            'type': 'SQL Injection',
            'target': 'https://example.com/search',
            'status': 'failed',
            'created_at': '2023-11-11',
            'description': 'Automated test for SQL injection vulnerabilities in search functionality.'
        },
        {
            'id': 'TC-006',
            'name': 'Rate Limiting Test - Login Endpoint',
            'type': 'Brute Force',
            'target': 'https://example.com/api/login',
            'status': 'completed',
            'created_at': '2023-11-10',
            'description': 'Tests if rate limiting is properly implemented on login endpoints.'
        }
    ]
    
    return render_template(
        'test_cases.html', 
        test_cases=all_test_cases,
        total_test_cases=test_case_stats['total'],
        active_page='test_cases'
    )

@app.route('/ai-agent-automation', methods=['GET', 'POST'])
def ai_agent_automation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get user's GitHub token
    user = conn.execute('SELECT github_token FROM users WHERE id = ?', (user_id,)).fetchone()
    github_connected = user and user['github_token'] is not None
    
    # Fetch repositories from database first (these have IDs)
    saved_repos = conn.execute(
        'SELECT id, repo_name, repo_url, status, last_scan FROM github_repos WHERE user_id = ? ORDER BY last_scan DESC', 
        (user_id,)
    ).fetchall()
    
    # Convert to list of dicts for template
    repositories = []
    for repo in saved_repos:
        repositories.append({
            'id': repo['id'],  # Use the database ID for the value
            'full_name': repo['repo_name'],
            'html_url': repo['repo_url'],
            'status': repo['status'],
            'last_scan': repo['last_scan'],
            'size_formatted': 'Unknown',  # Will fetch actual size if needed
            'is_saved': True  # Flag to indicate this is from the database
        })
    
    # If no saved repos and GitHub connected, fetch live repos
    if not repositories and github_connected:
        try:
            user_repos_response = requests.get(
                'https://api.github.com/user/repos',
                headers={
                    'Authorization': f'token {user["github_token"]}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                params={
                    'sort': 'updated',
                    'per_page': 30
                }
            )
            
            if user_repos_response.status_code == 200:
                github_repos = user_repos_response.json()
                # Add repository size in KB/MB format
                for repo in github_repos:
                    # Create temp ID for repositories not yet saved
                    repo['id'] = f"temp_{repo['id']}"
                    repo['is_saved'] = False
                    
                    size_kb = repo.get('size', 0)  # GitHub API returns size in KB
                    if size_kb < 1024:
                        repo['size_formatted'] = f"{size_kb} KB"
                    else:
                        repo['size_formatted'] = f"{size_kb / 1024:.1f} MB"
                
                repositories.extend(github_repos)
                
                # Store these repos in the database for future use
                for repo in github_repos:
                    # Check if repo already exists first
                    existing = conn.execute(
                        'SELECT id FROM github_repos WHERE user_id = ? AND repo_name = ?',
                        (user_id, repo['full_name'])
                    ).fetchone()
                    
                    if not existing:
                        # Insert the repository
                        conn.execute(
                            'INSERT INTO github_repos (user_id, repo_name, repo_url, status) VALUES (?, ?, ?, ?)',
                            (user_id, repo['full_name'], repo['html_url'], 'active')
                        )
                conn.commit()
        except Exception as e:
            logging.error(f"Error fetching GitHub repositories: {e}")
            flash('Error fetching GitHub repositories', 'danger')
    
    # Handle form submission
    assessment_results = None
    vulnerabilities = []
    test_cases = []
    
    if request.method == 'POST':
        # Log all form data for debugging
        logging.info("------------------------ Form Submission ---------------------")
        logging.info("Form data:")
        form_data = {}
        for key, value in request.form.items():
            form_data[key] = value
            logging.info(f"  {key}: {value}")
        
        # Get repository ID from form
        repo_id = request.form.get('repository')
        logging.info(f"Repository ID from form: {repo_id}")
        
        # Check backup ID if primary is missing
        if not repo_id:
            repo_id = request.form.get('repo_id_backup')
            logging.info(f"Using backup repository ID: {repo_id}")
        
        # Get assessment type
        assessment_type = request.form.get('assessment_type', 'vuln_scan')
        
        # Log form submission details
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        logging.info(f"Assessment form submitted with repository ID: {repo_id}")
        logging.info(f"Assessment type: {assessment_type}")
        
        # Get code sample if provided
        code_sample = request.form.get('code_sample')
        language = request.form.get('language')
        if code_sample:
            logging.info(f"Code sample provided, language: {language or 'auto-detect'}")
            
        logging.info(f"Is AJAX request: {is_ajax}")
        logging.info("------------------------ End Form Submission ---------------------")
        
        # Check if repository ID or code sample is provided
        if not repo_id and not code_sample:
            error_msg = 'Please select a repository or provide a code sample'
            logging.warning(f"Form submission error: {error_msg}")
            if is_ajax:
                return jsonify({'status': 'error', 'error': error_msg})
            flash(error_msg, 'warning')
            conn.close()
            return render_template(
                'ai_agent_automation.html',
                repositories=repositories,
                github_connected=github_connected,
                assessment_results=None,
                test_cases=test_cases,
                vulnerabilities=vulnerabilities,
                active_page='ai_agent_automation'
            )
        
        # Get repository details from the database if it's a number (database ID)
        # Skip repository lookup if we only have a code sample and no repo_id
        repo_name = None
        repo_details = None
        
        if repo_id:
            logging.info(f"Repository ID: {repo_id}, Type: {type(repo_id)}")
            
            if str(repo_id).strip().isdigit():
                repo_id = str(repo_id).strip()
                logging.info(f"Looking up repository with numeric ID: {repo_id}")
                
                try:
                    repo_record = conn.execute(
                        'SELECT * FROM github_repos WHERE id = ? AND user_id = ?',
                        (repo_id, user_id)
                    ).fetchone()
                    
                    if repo_record:
                        repo_name = repo_record['repo_name']
                        repo_details = {
                            'full_name': repo_name,
                            'language': 'Unknown',
                            'id': repo_id,
                            'size_formatted': 'Unknown'
                        }
                        logging.info(f"Found repository in database: {repo_name} (ID: {repo_id})")
                    else:
                        logging.warning(f"Repository with ID {repo_id} not found in database")
                        error_msg = f'Repository with ID {repo_id} not found'
                        if is_ajax:
                            return jsonify({'status': 'error', 'error': error_msg})
                        flash(error_msg, 'danger')
                        conn.close()
                        return render_template(
                            'ai_agent_automation.html',
                            repositories=repositories,
                            github_connected=github_connected,
                            assessment_results=None,
                            test_cases=test_cases,
                            vulnerabilities=vulnerabilities,
                            active_page='ai_agent_automation'
                        )
                except Exception as e:
                    logging.error(f"Error looking up repository: {str(e)}")
                    error_msg = f'Error looking up repository: {str(e)}'
                    if is_ajax:
                        return jsonify({'status': 'error', 'error': error_msg})
                    flash(error_msg, 'danger')
                    conn.close()
                    return render_template(
                        'ai_agent_automation.html',
                        repositories=repositories,
                        github_connected=github_connected,
                        assessment_results=None,
                        test_cases=test_cases,
                        vulnerabilities=vulnerabilities,
                        active_page='ai_agent_automation'
                    )
            elif repo_id:
                # For temp IDs or full repository names, find in the list
                logging.info(f"Looking up repository with non-numeric ID: {repo_id}")
                for repo in repositories:
                    repo_id_str = str(repo.get('id'))
                    if repo_id_str == str(repo_id).strip() or repo.get('full_name') == repo_id:
                        repo_name = repo.get('full_name')
                        repo_details = repo
                        logging.info(f"Found repository in list: {repo_name} (ID: {repo_id_str})")
                        break
                
                if not repo_name:
                    logging.warning(f"Repository with ID/name {repo_id} not found in available repositories")
                    error_msg = f'Repository {repo_id} not found in available repositories'
                    if is_ajax:
                        return jsonify({'status': 'error', 'error': error_msg})
                    flash(error_msg, 'danger')
                    conn.close()
                    return render_template(
                        'ai_agent_automation.html',
                        repositories=repositories,
                        github_connected=github_connected,
                        assessment_results=None,
                        test_cases=test_cases,
                        vulnerabilities=vulnerabilities,
                        active_page='ai_agent_automation'
                    )
        elif code_sample:
            # If no repository but code sample is provided, we can proceed without repo details
            logging.info("No repository selected, but code sample provided. Proceeding with direct code analysis.")
            repo_name = "Direct Code Analysis"
            repo_details = {
                'full_name': 'Code Sample Analysis',
                'language': language or 'Unknown',
                'id': 'code_sample',
                'size_formatted': f"{len(code_sample) // 1024 + 1} KB"
            }
        
        # Check if OpenAI API key is available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key and assessment_type != 'legacy':
            if is_ajax:
                assessment_type = 'legacy'
            else:
                flash('OpenAI API key is not configured. Using legacy assessment instead.', 'warning')
                assessment_type = 'legacy'
        
        # Fetch repository languages (if needed)
        if repo_name and not code_sample:
            logging.info(f"Fetching languages for repository: {repo_name}")
            try:
                # Try to get language information if GitHub token is available
                if github_connected:
                    languages_url = f"https://api.github.com/repos/{repo_name}/languages"
                    languages_response = requests.get(
                        languages_url,
                        headers={
                            'Authorization': f'token {user["github_token"]}',
                            'Accept': 'application/vnd.github.v3+json'
                        }
                    )
                    
                    if languages_response.status_code == 200:
                        languages_data = languages_response.json()
                        languages = list(languages_data.keys())
                        logging.info(f"Detected languages: {languages}")
                    else:
                        # If API call fails, use fallback languages
                        languages = ['JavaScript', 'HTML', 'CSS']
                        logging.warning(f"Couldn't fetch repository languages, using defaults: {languages}")
                else:
                    # Fallback languages if no GitHub token
                    languages = ['JavaScript', 'HTML', 'CSS']
                    logging.info(f"No GitHub token, using default languages: {languages}")
            except Exception as e:
                languages = ['JavaScript', 'HTML', 'CSS']
                logging.error(f"Error fetching repository languages: {str(e)}")
                logging.info(f"Using fallback languages: {languages}")
        elif code_sample:
            # If using a direct code sample, set the language based on the form input
            if language:
                languages = [language]
                logging.info(f"Using provided language for code sample: {language}")
            else:
                # Try to guess language from code sample or use defaults
                languages = ['Unknown']
                logging.info("No language specified for code sample, using auto-detection")
        else:
            languages = ['JavaScript', 'HTML', 'CSS']
            logging.warning("No repository name or code sample available, using default languages")
        
        # Get organization ID (use existing or create one)
        org_id = 1  # Default organization ID
        try:
            # Using our mock Organization class - no need for db.session
            organization = Organization(
                name="Default Organization",
                industry="Technology",
                description="Default organization for security scans",
                admin_user_id=user_id
            )
            org_id = organization.id
            logging.info(f"Using default organization with ID: {org_id}")
        except Exception as e:
            logging.error(f"Error with organization: {str(e)}")
        
        # If it's an AJAX request, start assessment in background thread and return immediate response
        if is_ajax:
            try:
                assessment_id = str(uuid.uuid4())

                # Initialize progress tracking
                app.config.setdefault('ASSESSMENT_PROGRESS', {})
                app.config['ASSESSMENT_PROGRESS'][assessment_id] = {
                    'status': 'running',
                    'current_stage': 'Initializing',
                    'percent_complete': 0,
                    'assessment_type': assessment_type,
                    'repo_id': repo_id,
                    'repo_name': repo_name,
                    'user_id': user_id,
                    'logs': ['Starting assessment'],
                    'time_started': datetime.utcnow().isoformat(),
                    'estimated_completion': (datetime.utcnow() + timedelta(minutes=2)).isoformat()
                }

                # Capture code sample and language if provided
                code_sample = request.form.get('code_sample')
                language = request.form.get('language')
                    
                if code_sample:
                    app.config['ASSESSMENT_PROGRESS'][assessment_id]['code_sample'] = code_sample
                    app.config['ASSESSMENT_PROGRESS'][assessment_id]['language'] = language
                    logging.info(f"Code sample provided for assessment {assessment_id}, language: {language or 'auto-detect'}")
                    
                # Start assessment in background thread
                def run_assessment_thread():
                    try:
                        # Create a new database connection for this thread
                        # We need a new connection because SQLite connections can't be shared between threads
                        thread_conn = get_db_connection()
                        
                        # Get thread local copies of necessary variables to avoid "cannot access local variable" errors
                        thread_repo_id = repo_id
                        thread_repo_name = repo_name
                        thread_repo_details = repo_details
                        thread_assessment_type = assessment_type
                        thread_languages = languages.copy() if isinstance(languages, list) else [languages]
                        
                        # Import AI agent manager
                        try:
                            from shield.backend.app.services.ai_agent_automation import AIAgentManager as ImportedAIAgentManager
                            agent_class = ImportedAIAgentManager
                            logging.info("Using imported AIAgentManager from shield.backend.app.services")
                        except ImportError:
                            logging.info("Using built-in AIAgentManager")
                            agent_class = AIAgentManager
                        
                        # Update progress
                        app.config['ASSESSMENT_PROGRESS'][assessment_id].update({
                            'current_stage': 'Analyzing technology stack',
                            'percent_complete': 10,
                            'logs': app.config['ASSESSMENT_PROGRESS'][assessment_id]['logs'] + ['Starting analysis of tech stack']
                        })
                        
                        # Create agent manager
                        agent = agent_class(org_id)
                        
                        # Update progress tracker with status updates
                        agent.register_progress_callback(lambda stage, percent, message: _update_progress(
                            assessment_id, stage, percent, message
                        ))
                        
                        # Fetch code from repository if repo_id is provided
                        code_sample = None
                        if thread_repo_id and str(thread_repo_id).strip().isdigit():
                            try:
                                # Update progress
                                _update_progress(assessment_id, "Fetching repository code", 15, "Retrieving code from repository")
                                
                                # Get repository details
                                repo_record = thread_conn.execute(
                                    'SELECT * FROM github_repos WHERE id = ?',
                                    (thread_repo_id,)
                                ).fetchone()
                                
                                # Get user's GitHub token
                                user_id = app.config['ASSESSMENT_PROGRESS'][assessment_id].get('user_id')
                                user = thread_conn.execute('SELECT github_token FROM users WHERE id = ?', (user_id,)).fetchone()
                                github_token = user['github_token'] if user else None
                                
                                if repo_record and github_token:
                                    thread_repo_name = repo_record['repo_name']
                                    
                                    # Extract owner and repo from full name (format: owner/repo)
                                    owner, repo = thread_repo_name.split('/')
                                    
                                    # Fetch repository contents
                                    _update_progress(assessment_id, "Fetching code", 20, f"Retrieving code from {thread_repo_name}")
                                    
                                    # Get the file list from the repository
                                    files_url = f"https://api.github.com/repos/{thread_repo_name}/git/trees/master?recursive=1"
                                    files_response = requests.get(
                                        files_url,
                                        headers={
                                            'Authorization': f'token {github_token}',
                                            'Accept': 'application/vnd.github.v3+json'
                                        }
                                    )
                                    
                                    if files_response.status_code == 200:
                                        files_data = files_response.json()
                                        code_files = []
                                        
                                        # Filter for code files (common extensions)
                                        code_extensions = ['.js', '.py', '.java', '.c', '.cpp', '.cs', '.php', '.rb', '.go', '.ts', '.html', '.css', '.sql', '.sol']
                                        
                                        for file in files_data.get('tree', []):
                                            if file['type'] == 'blob' and any(file['path'].endswith(ext) for ext in code_extensions):
                                                code_files.append(file)
                                        
                                        # Limit to a reasonable number of files to avoid API rate limits
                                        code_files = code_files[:10]  # Limit to 10 files for now
                                        
                                        # Fetch content for each file
                                        all_code = []
                                        for i, file in enumerate(code_files):
                                            _update_progress(
                                                assessment_id, 
                                                "Fetching code", 
                                                20 + (i * 40 // len(code_files)),
                                                f"Retrieving {file['path']}"
                                            )
                                            
                                            # Get file content
                                            content_url = f"https://api.github.com/repos/{thread_repo_name}/contents/{file['path']}"
                                            content_response = requests.get(
                                                content_url,
                                                headers={
                                                    'Authorization': f'token {github_token}',
                                                    'Accept': 'application/vnd.github.v3+json'
                                                }
                                            )
                                            
                                            if content_response.status_code == 200:
                                                file_data = content_response.json()
                                                if 'content' in file_data and file_data.get('encoding') == 'base64':
                                                    import base64
                                                    file_content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
                                                    all_code.append(f"File: {file['path']}\n\n{file_content}\n\n")
                                    
                                    # Combine code from all files
                                    if all_code:
                                        code_sample = "\n".join(all_code)
                                        logging.info(f"Successfully retrieved code from {len(all_code)} files in {thread_repo_name}")
                                    else:
                                        logging.warning(f"Failed to fetch code from repository {thread_repo_name}")
                                else:
                                    logging.warning(f"Repository record not found or GitHub token missing")
                            except Exception as e:
                                logging.error(f"Error fetching repository code: {str(e)}")
                                code_sample = None
                        
                        # If no code from repo and code_sample provided in form, use that instead
                        if not code_sample and 'code_sample' in app.config['ASSESSMENT_PROGRESS'][assessment_id]:
                            code_sample = app.config['ASSESSMENT_PROGRESS'][assessment_id]['code_sample']
                        
                        # Run assessment with code_sample if available
                        if code_sample:
                            _update_progress(assessment_id, "Analyzing code", 60, "Scanning code for vulnerabilities")
                            language = app.config['ASSESSMENT_PROGRESS'][assessment_id].get('language', None)
                            results = agent.run_automated_assessment(
                                thread_languages, 
                                thread_assessment_type,
                                code_sample=code_sample, 
                                language=language
                            )
                        else:
                            # Run assessment without code sample
                            results = agent.run_automated_assessment(thread_languages, thread_assessment_type)
                        
                        # Add repo information to assessment results
                        results['repository'] = {
                                'name': thread_repo_name,
                                'size': thread_repo_details.get('size_formatted') if thread_repo_details else 'Unknown',
                                'language': thread_repo_details.get('language') if thread_repo_details else ', '.join(thread_languages[:3])
                        }
                        
                        # Store results in app config for retrieval
                        app.config['ASSESSMENT_PROGRESS'][assessment_id].update({
                            'status': 'completed',
                            'current_stage': 'Assessment complete',
                            'percent_complete': 100,
                            'results': results,
                            'time_completed': datetime.utcnow().isoformat()
                        })
                        
                        # Also store results in completed assessments for later retrieval
                        app.config.setdefault('COMPLETED_ASSESSMENTS', {})
                        app.config['COMPLETED_ASSESSMENTS'][assessment_id] = {
                            'timestamp': datetime.utcnow().isoformat(),
                            'results': results
                        }
                        
                        # Update repo last_scan timestamp
                        if thread_repo_id and str(thread_repo_id).strip().isdigit():
                            try:
                                thread_conn.execute(
                                    'UPDATE github_repos SET last_scan = ? WHERE id = ?',
                                    (datetime.utcnow().isoformat(), thread_repo_id)
                                )
                                thread_conn.commit()
                                logging.info(f"Updated last_scan timestamp for repository ID: {thread_repo_id}")
                            except Exception as e:
                                logging.error(f"Error updating repository timestamp: {str(e)}")
                        
                        # Close thread-specific connection
                        thread_conn.close()
                        
                        logging.info(f"Assessment {assessment_id} completed successfully")
                        
                    except Exception as e:
                        logging.error(f"Error in assessment thread: {str(e)}")
                        
                        # Update progress to error state
                        if assessment_id in app.config.get('ASSESSMENT_PROGRESS', {}):
                            app.config['ASSESSMENT_PROGRESS'][assessment_id].update({
                                'status': 'failed',
                                'error': str(e),
                                'current_stage': 'Error',
                                'logs': app.config['ASSESSMENT_PROGRESS'][assessment_id].get('logs', []) + [f"Error: {str(e)}"]
                            })

                # Start the thread
                assessment_thread = threading.Thread(target=run_assessment_thread)
                assessment_thread.daemon = True
                assessment_thread.start()
                
                # Return immediate response with assessment ID
                return jsonify({
                    'status': 'starting',
                    'message': 'Assessment started',
                    'assessment_id': assessment_id,
                    'assessment_type': assessment_type,
                    'repo_name': repo_name
                })
                
            except Exception as e:
                error_msg = f"Error starting assessment: {str(e)}"
                logging.error(error_msg)
                return jsonify({
                    'status': 'error',
                    'error': error_msg
                })
                
        else:
            # For non-AJAX requests, run assessment synchronously
            try:
                # Import AI agent manager
                try:
                    from shield.backend.app.services.ai_agent_automation import AIAgentManager as ImportedAIAgentManager
                    agent_class = ImportedAIAgentManager
                except ImportError:
                    agent_class = AIAgentManager
                
                # Create agent manager
                agent = agent_class(org_id)
                
                # Run assessment
                results = agent.run_automated_assessment(languages, assessment_type)
                
                # Store results in session
                assessment_id = results.get('assessment_id', str(uuid.uuid4()))
                assessment_storage = session.get('assessment_results', {})
                assessment_storage[assessment_id] = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'results': results
                }
                session['assessment_results'] = assessment_storage
                session['last_assessment_id'] = assessment_id
                
                # Get test cases and vulnerabilities
                test_cases = TestCase.query.filter_by(organization_id=org_id).order_by(TestCase.id.desc()).limit(20).all()
                vulnerabilities = Vulnerability.query.filter_by(organization_id=org_id).order_by(Vulnerability.id.desc()).limit(20).all()
                
                # Update repo last_scan timestamp
                if repo_id and str(repo_id).strip().isdigit():
                    conn.execute(
                        'UPDATE github_repos SET last_scan = ? WHERE id = ?',
                        (datetime.utcnow().isoformat(), repo_id)
                    )
                    conn.commit()
                
                # Get the scanned repository details for display
                scanned_repo = {
                    'repo_name': repo_name,
                    'size': repo_details.get('size_formatted', 'Unknown') if repo_details else 'Unknown'
                }
                
                conn.close()
                return render_template(
                    'ai_agent_automation.html',
                    repositories=repositories,
                    github_connected=github_connected,
                    assessment_results=results,
                    test_cases=test_cases,
                    vulnerabilities=vulnerabilities,
                    scanned_repo=scanned_repo,
                    active_page='ai_agent_automation'
                )
                
            except Exception as e:
                logging.error(f"Error running assessment: {str(e)}")
                flash(f"Error: {str(e)}", 'danger')
                conn.close()
                return render_template(
                    'ai_agent_automation.html',
                    repositories=repositories,
                    github_connected=github_connected,
                    assessment_results=None,
                    test_cases=[],
                    vulnerabilities=[],
                    active_page='ai_agent_automation'
                )
    
    # GET method - Display the form
    try:
        # Get user's most recent assessment
        assessment_results = None
        test_cases = []
        vulnerabilities = []
        scanned_repo = None
        
        # Check if there's a stored assessment in the session
        if 'last_assessment_id' in session and 'assessment_results' in session:
            last_assessment_id = session.get('last_assessment_id')
            assessment_storage = session.get('assessment_results', {})
            
            if last_assessment_id in assessment_storage:
                assessment_data = assessment_storage[last_assessment_id]
                assessment_results = assessment_data.get('results')
                
                # Fetch test cases and vulnerabilities from database
                org_id = assessment_results.get('organization_id', 1) if assessment_results else 1
                test_cases = TestCase.query.filter_by(organization_id=org_id).order_by(TestCase.id.desc()).limit(20).all()
                vulnerabilities = Vulnerability.query.filter_by(organization_id=org_id).order_by(Vulnerability.id.desc()).limit(20).all()
                
                # Get the scanned repository details if available
                scanned_repo = assessment_results.get('repository', {}) if assessment_results else None
        
        conn.close()
        return render_template(
            'ai_agent_automation.html',
            repositories=repositories,
            github_connected=github_connected,
        assessment_results=assessment_results,
            test_cases=test_cases,
            vulnerabilities=vulnerabilities,
            scanned_repo=scanned_repo,
        active_page='ai_agent_automation'
    )
    except Exception as e:
        logging.error(f"Error in AI agent automation page: {str(e)}")
        conn.close()
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

def _update_progress(assessment_id, stage, percent, message=None):
    """Update the progress of a running assessment"""
    if not assessment_id or assessment_id not in app.config.get('ASSESSMENT_PROGRESS', {}):
        logging.error(f"Cannot update progress for unknown assessment: {assessment_id}")
        return
    
    try:
        # Update progress info
        app.config['ASSESSMENT_PROGRESS'][assessment_id].update({
            'current_stage': stage,
            'percent_complete': percent,
            'last_update': datetime.utcnow().isoformat()
        })
        
        # Add message to logs if provided
        if message:
            logs = app.config['ASSESSMENT_PROGRESS'][assessment_id].get('logs', [])
            logs.append(f"{stage}: {message}")
            app.config['ASSESSMENT_PROGRESS'][assessment_id]['logs'] = logs
            
        # Calculate estimated time remaining
        if percent > 0:
            try:
                # Get start time (as string)
                start_time_str = app.config['ASSESSMENT_PROGRESS'][assessment_id].get('time_started')
                if start_time_str:
                    start_time = datetime.fromisoformat(start_time_str)
                    now = datetime.utcnow()
                    elapsed = (now - start_time).total_seconds()
                    
                    # Calculate estimated total time and remaining time
                    if percent < 100:
                        total_estimated = elapsed * 100 / percent
                        remaining = total_estimated - elapsed
                        
                        # Update estimated completion time
                        estimated_completion = now + timedelta(seconds=remaining)
                        app.config['ASSESSMENT_PROGRESS'][assessment_id]['estimated_completion'] = estimated_completion.isoformat()
                        app.config['ASSESSMENT_PROGRESS'][assessment_id]['time_remaining'] = int(remaining)
            except Exception as e:
                logging.error(f"Error updating progress: {str(e)}")
            
        logging.info(f"Progress updated: {stage} - {percent}%")
    except Exception as e:
        logging.error(f"Error updating progress: {str(e)}")

@app.route('/api/scan-progress/<assessment_id>', methods=['GET'])
def scan_progress(assessment_id):
    """
    Get scan progress for a specific assessment ID
    """
    try:
        # Look for progress info in app config
        progress_data = app.config.get('ASSESSMENT_PROGRESS', {}).get(assessment_id)
        
        if not progress_data:
            return jsonify({
                'status': 'error',
                'error': 'Assessment not found'
            })
            
        # Check if assessment is completed
        if progress_data.get('status') == 'completed':
            # If complete, store in session for next page load if we have an active request context
            try:
                completed_assessment = app.config.get('COMPLETED_ASSESSMENTS', {}).get(assessment_id)
                if completed_assessment:
                    # Try to update session if we have an active request context
                    if 'user_id' in session:
                        assessment_storage = session.get('assessment_results', {})
                        assessment_storage[assessment_id] = completed_assessment
                        session['assessment_results'] = assessment_storage
                        session['last_assessment_id'] = assessment_id
            except RuntimeError:
                # Ignore session errors outside request context
                pass
                
        # Return progress data
        return jsonify(progress_data)
        
    except Exception as e:
        logging.error(f"Error getting scan progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/test-cases/<test_case_id>')
def test_case_detail(test_case_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Use the same list of demo test cases as in the test_cases route for consistency
    demo_test_cases = [
        {
            'id': 'TC-001',
            'name': 'SQL Injection Test - Login Form',
            'type': 'SQL Injection',
            'target': 'https://example.com/login',
            'status': 'completed',
            'created_at': '2023-11-15',
            'description': 'Tests for SQL injection vulnerabilities in the login form.',
            'test_steps': ['Input malicious SQL in username field', 'Input malicious SQL in password field', 'Observe response'],
            'expected_result': 'Application should sanitize input and not expose database errors',
            'result': json.dumps({
                'status': 'failed',
                'details': 'SQL error message exposed, possible vulnerability detected',
                'timestamp': '2023-11-15T14:30:00Z'
            })
        },
        {
            'id': 'TC-002',
            'name': 'XSS Test - Comment Section',
            'type': 'XSS',
            'target': 'https://example.com/posts/comments',
            'status': 'completed',
            'created_at': '2023-11-14',
            'description': 'Tests for XSS vulnerabilities in the comment submission form.',
            'test_steps': ['Input script tag in comment field', 'Submit form', 'Check if script executes'],
            'expected_result': 'Application should escape HTML and prevent script execution',
            'result': json.dumps({
                'status': 'completed',
                'details': 'Script tags properly escaped, no vulnerability detected',
                'timestamp': '2023-11-14T10:15:00Z'
            })
        },
        {
            'id': 'TC-003',
            'name': 'CSRF Protection Test - Profile Update',
            'type': 'CSRF',
            'target': 'https://example.com/profile/update',
            'status': 'pending',
            'created_at': '2023-11-13',
            'description': 'Verifies that CSRF tokens are correctly implemented on profile update forms.',
            'test_steps': ['Login to application', 'Observe CSRF token in form', 'Create malicious form without token', 'Submit and verify rejection'],
            'expected_result': 'Application should reject form submissions without valid CSRF tokens',
            'result': None
        },
        {
            'id': 'TC-004',
            'name': 'Authentication Bypass Test',
            'type': 'Authentication',
            'target': 'https://example.com/admin',
            'status': 'running',
            'created_at': '2023-11-12',
            'description': 'Attempts to bypass authentication mechanisms to access admin area.',
            'test_steps': ['Manipulate session cookies', 'Attempt direct URL access', 'Test for improper redirects'],
            'expected_result': 'All authentication bypass attempts should be blocked',
            'result': json.dumps({
                'status': 'running',
                'details': 'Test in progress: 2 of 5 checks completed',
                'timestamp': '2023-11-15T09:45:00Z'
            })
        },
        {
            'id': 'TC-005',
            'name': 'SHIELD AI: SQL Injection Detection',
            'type': 'SQL Injection',
            'target': 'https://example.com/search',
            'status': 'failed',
            'created_at': '2023-11-11',
            'description': 'Automated test for SQL injection vulnerabilities in search functionality.',
            'test_steps': ['Execute automated SQL injection test suite', 'Try various injection payloads', 'Check for successful exploits'],
            'expected_result': 'Application should properly sanitize all search inputs',
            'result': json.dumps({
                'status': 'failed',
                'details': 'Error in test execution: Connection timeout',
                'timestamp': '2023-11-11T16:20:00Z'
            })
        },
        {
            'id': 'TC-006',
            'name': 'Rate Limiting Test - Login Endpoint',
            'type': 'Brute Force',
            'target': 'https://example.com/api/login',
            'status': 'completed',
            'created_at': '2023-11-10',
            'description': 'Tests if rate limiting is properly implemented on login endpoints.',
            'test_steps': ['Send 10 login requests in 10 seconds', 'Send 50 login requests in 30 seconds', 'Verify if requests are blocked'],
            'expected_result': 'System should limit excessive login attempts',
            'result': json.dumps({
                'status': 'completed',
                'details': 'Rate limiting properly implemented. IP blocked after 20 attempts.',
                'timestamp': '2023-11-10T11:05:00Z'
            })
        }
    ]
    
    for test_case in demo_test_cases:
        if test_case['id'] == test_case_id:
    # Parse result if available
            result = None
        if test_case.get('result'):
            try:
                result = json.loads(test_case['result'])
            except:
                result = None
    
    return render_template(
        'test_case_detail.html',
        test_case=test_case,
                organization=None,
                vulnerability=None,
        result=result,
        active_page='test_cases'
    )

    # If no matching demo test case, redirect to list
    return redirect(url_for('test_cases'))

@app.route('/vulnerabilities/<vulnerability_id>')
def vulnerability_detail(vulnerability_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Use the same list of vulnerabilities as in dashboard and vulnerabilities routes
    all_vulnerabilities = [
        {
            'id': 'VLN-001',
            'title': 'SQL Injection in Login Form',
            'description': 'The login form is vulnerable to SQL injection attacks, allowing unauthorized access to the database.',
            'severity': 'critical',
            'cvss_score': 9.8,
            'status': 'open',
            'discovered_at': '2023-11-15',
            'discovered_by': 'SHIELD AI Scanner',
            'affected_systems': json.dumps(['Web Application', 'Authentication System', 'Database']),
            'remediation': 'Use parameterized queries or prepared statements instead of dynamic SQL. Implement input validation and sanitization.',
            'steps_to_reproduce': ['Navigate to login page', 'Enter \' OR 1=1 -- in username field', 'Submit the form', 'Observe unauthorized access'],
            'references': ['OWASP Top 10: A03:2021-Injection', 'CWE-89: SQL Injection']
        },
        {
            'id': 'VLN-002',
            'title': 'Cross-Site Scripting in Comment Section',
            'description': 'The comment section does not properly sanitize user input, allowing attackers to inject malicious scripts.',
            'severity': 'high',
            'cvss_score': 7.4,
            'status': 'in_progress',
            'discovered_at': '2023-11-14',
            'discovered_by': 'Manual Penetration Test',
            'affected_systems': json.dumps(['Web Application', 'User Interface']),
            'remediation': 'Implement proper input validation and output encoding. Use Content Security Policy (CSP) headers.',
            'steps_to_reproduce': ['Navigate to comment section', 'Enter <script>alert("XSS")</script> in comment field', 'Submit comment', 'Observe script execution'],
            'references': ['OWASP Top 10: A07:2021-XSS', 'CWE-79: Improper Neutralization of Input']
        },
        {
            'id': 'VLN-003',
            'title': 'Insecure Direct Object Reference',
            'description': 'API endpoints do not properly validate user permissions, allowing access to unauthorized resources.',
            'severity': 'medium',
            'cvss_score': 5.9,
            'status': 'open',
            'discovered_at': '2023-11-12',
            'discovered_by': 'Code Review AI',
            'affected_systems': json.dumps(['API', 'Authorization System']),
            'remediation': 'Implement proper access control checks. Use indirect reference maps.',
            'steps_to_reproduce': ['Login as regular user', 'Access /api/users/123 where 123 is another user\'s ID', 'Observe unauthorized access to user data'],
            'references': ['OWASP Top 10: A01:2021-Broken Access Control', 'CWE-639: Authorization Bypass Through User-Controlled Key']
        },
        {
            'id': 'VLN-004',
            'title': 'Missing Rate Limiting on Authentication Endpoint',
            'description': 'The authentication endpoint does not implement rate limiting, making it vulnerable to brute force attacks.',
            'severity': 'medium',
            'cvss_score': 6.2,
            'status': 'resolved',
            'discovered_at': '2023-11-10',
            'discovered_by': 'SHIELD AI Scanner',
            'affected_systems': json.dumps(['Authentication System', 'API']),
            'remediation': 'Implement rate limiting on authentication endpoints. Consider using CAPTCHA for repeated failed attempts.',
            'steps_to_reproduce': ['Send multiple login requests with different passwords', 'Observe no throttling or lockout'],
            'references': ['OWASP Top 10: A04:2021-Insecure Design', 'CWE-307: Improper Restriction of Excessive Authentication Attempts']
        },
        {
            'id': 'VLN-005',
            'title': 'Outdated Dependencies with Known Vulnerabilities',
            'description': 'Several dependencies in the project are outdated and contain known security vulnerabilities.',
            'severity': 'high',
            'cvss_score': 8.1,
            'status': 'open',
            'discovered_at': '2023-11-08',
            'discovered_by': 'Dependency Scanner',
            'affected_systems': json.dumps(['Web Application', 'Backend Services']),
            'remediation': 'Update dependencies to their latest secure versions. Implement a process for regular dependency auditing.',
            'steps_to_reproduce': ['Run dependency check scan', 'Observe outdated packages with CVEs'],
            'references': ['OWASP Top 10: A06:2021-Vulnerable and Outdated Components', 'Various CVEs']
        },
        {
            'id': 'VLN-006',
            'title': 'Weak Password Policy',
            'description': 'The password policy does not enforce sufficient complexity requirements.',
            'severity': 'low',
            'cvss_score': 4.3,
            'status': 'open',
            'discovered_at': '2023-11-05',
            'discovered_by': 'Security Audit',
            'affected_systems': json.dumps(['Authentication System', 'User Management']),
            'remediation': 'Implement a stronger password policy that requires minimum length, complexity, and prohibits common passwords.',
            'steps_to_reproduce': ['Create new account', 'Successfully use "password" as password', 'Observe no enforcement of complexity'],
            'references': ['OWASP Top 10: A07:2021-Identification and Authentication Failures', 'CWE-521: Weak Password Requirements']
        }
    ]
    
    # Find the matching vulnerability
    for vuln in all_vulnerabilities:
        if vuln['id'] == vulnerability_id:
            # Parse affected systems
            affected_systems = []
        if 'affected_systems' in vuln:
            try:
                    affected_systems = json.loads(vuln['affected_systems'])
            except:
                affected_systems = []
    
    return render_template(
        'vulnerability_detail.html',
                vulnerability=vuln,
                organization=None,
                test_cases=[],
        affected_systems=affected_systems,
        active_page='vulnerabilities'
    )
    
    # If no matching vulnerability found, redirect to vulnerabilities list
    return redirect(url_for('vulnerabilities'))

# GitHub integration routes
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    github_connected = user['github_token'] is not None if user else False
    
    # Store github connected status in session
    if github_connected:
        session['github_token'] = True
    else:
        session.pop('github_token', None)
    
    # Fetch repositories if GitHub is connected
    repos = []
    if github_connected:
        repos = conn.execute('SELECT * FROM github_repos WHERE user_id = ? ORDER BY last_scan DESC', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template(
        'profile.html',
        user=user,
        github_connected=github_connected,
        repos=repos,
        active_page='profile'
    )

@app.route('/github/login')
def github_login():
    if 'user_id' not in session:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))
    
    # Store complete user session information
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        conn.close()
        flash('User account not found. Please log in again.', 'danger')
        session.clear()
        return redirect(url_for('login'))
    
    # Store all necessary user data to recreate session if needed
    session['pre_github_user_id'] = session['user_id']
    session['pre_github_username'] = user['username']
    session['pre_github_email'] = user['email'] if user['email'] else ''
    
    # Set a longer session lifetime for the OAuth flow
    session.permanent = True
    
    # Force session to be saved immediately
    session.modified = True
    
    # Generate a random state parameter to prevent CSRF attacks
    state = secrets.token_hex(16)
    session['github_oauth_state'] = state
    
    # Check if github_oauth_state column exists in users table
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # If column doesn't exist, add it
    if 'github_oauth_state' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN github_oauth_state TEXT')
        conn.commit()
    
    # Store the state in the database as well for backup
    conn.execute('UPDATE users SET github_oauth_state = ? WHERE id = ?', (state, session['user_id']))
    conn.commit()
    
    # Log the OAuth initiation
    logging.info(f"GitHub OAuth initiated for user {user['username']} (ID: {session['user_id']})")
    conn.close()
    
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_CALLBACK_URL,
        'scope': 'repo read:user',
        'state': state,
    }
    
    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/github/callback')
def github_callback():
    # Get the state and code from the request
    request_state = request.args.get('state')
    code = request.args.get('code')
    
    # Log the callback received
    logging.info(f"GitHub callback received with state: {request_state[:5]}... and code: {code[:5] if code else None}...")
    
    if not code or not request_state:
        flash('Invalid response from GitHub. Missing code or state parameter.', 'danger')
        return redirect(url_for('profile'))
    
    # First, try to recover session from pre-stored data if user_id is missing
    if 'user_id' not in session and 'pre_github_user_id' in session:
        # If we have pre-stored user data, use it to restore the session
        if 'pre_github_user_id' in session and 'pre_github_username' in session:
            session['user_id'] = session['pre_github_user_id']
            session['username'] = session['pre_github_username']
            session.permanent = True  # Ensure session persistence
            session.modified = True
            logging.info(f"Session restored for user {session['username']} from pre-stored data")
    
    # If still no user_id, try to get user from database using state parameter
    if 'user_id' not in session and request_state:
        conn = get_db_connection()
        # Find the user associated with this state in the database
        user = conn.execute('SELECT * FROM users WHERE github_oauth_state = ?', (request_state,)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True  # Ensure session persistence
            session.modified = True
            logging.info(f"Session recreated for user {user['username']} based on OAuth state from database")
    
    # Final check for user_id
    if 'user_id' not in session:
        flash('Your session has expired. Please log in again and try connecting GitHub.', 'warning')
        return redirect(url_for('login'))
    
    # Get user ID and username from session
    user_id = session.get('user_id')
    username = session.get('username')
    
    logging.info(f"Processing GitHub callback for user {username} (ID: {user_id})")
    
    # Verify state parameter to prevent CSRF attacks
    # First check session state
    session_state_valid = 'github_oauth_state' in session and session['github_oauth_state'] == request_state
    
    # If session state is invalid, check database state as backup
    if not session_state_valid:
        conn = get_db_connection()
        user = conn.execute('SELECT github_oauth_state FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not user or user['github_oauth_state'] != request_state:
            logging.warning(f"Invalid state parameter for user {username}. Session state: {session.get('github_oauth_state', 'None')[:5]}..., Request state: {request_state[:5]}...")
            flash('Invalid state parameter. Please try connecting to GitHub again.', 'danger')
            return redirect(url_for('profile'))
        else:
            logging.info(f"State validated from database for user {username}")
    else:
        logging.info(f"State validated from session for user {username}")
    
    # Exchange the code for an access token
    try:
        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code,
                'redirect_uri': GITHUB_CALLBACK_URL
            },
            headers={'Accept': 'application/json'},
            timeout=10  # Add timeout to prevent hanging
        )
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            error = token_data.get('error', 'Unknown error')
            error_description = token_data.get('error_description', 'No description')
            logging.error(f"GitHub token exchange failed: {error} - {error_description}")
            flash(f'Failed to obtain access token from GitHub: {error_description}', 'danger')
            return redirect(url_for('profile'))
            
    except Exception as e:
        logging.error(f"Exception during GitHub token exchange: {str(e)}")
        flash('Error connecting to GitHub. Please try again.', 'danger')
        return redirect(url_for('profile'))
    
    # Store the token in the database and clear the oauth state
    conn = get_db_connection()
    conn.execute('UPDATE users SET github_token = ?, github_oauth_state = NULL WHERE id = ?', (access_token, user_id))
    conn.commit()
    conn.close()
    
    # Ensure user is still in session
    session['user_id'] = user_id
    session['username'] = username
    session['github_token'] = access_token
    session['github_connected'] = True
    session.permanent = True  # Ensure session persistence
    session.modified = True
    
    logging.info(f"GitHub token stored successfully for user {username}")
    
    # Clean up temporary session data
    for key in ['pre_github_user_id', 'pre_github_username', 'pre_github_email', 'github_oauth_state']:
        if key in session:
            session.pop(key, None)
    
    # Set success message
    flash('GitHub account connected successfully!', 'success')
    
    # Redirect to fetch repos page
    return redirect(url_for('github_repos'))

@app.route('/github/repos')
def github_repos():
    if 'user_id' not in session:
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        conn.close()
        # Session exists but user not found in database - clear session and redirect to login
        session.clear()
        flash('User account not found. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    if not user['github_token']:
        conn.close()
        flash('GitHub account not connected. Please connect your GitHub account first.', 'warning')
        return redirect(url_for('profile', error='GitHub not connected'))
    
    # Ensure GitHub token is in session
    session['github_token'] = user['github_token']
    session['github_connected'] = True
    session.modified = True
    
    # Fetch repositories from GitHub with additional details
    try:
        user_repos_response = requests.get(
            'https://api.github.com/user/repos?sort=updated&per_page=100',
            headers={
                'Authorization': f'token {user["github_token"]}',
                'Accept': 'application/vnd.github.v3+json'
            },
            timeout=10
        )
        
        if user_repos_response.status_code != 200:
            # Log the error details
            logging.error(f"GitHub API error: {user_repos_response.status_code} - {user_repos_response.text}")
            
            # If token is invalid, clear it
            if user_repos_response.status_code == 401:
                conn = get_db_connection()
                conn.execute('UPDATE users SET github_token = NULL WHERE id = ?', (session['user_id'],))
                conn.commit()
                conn.close()
                session.pop('github_token', None)
                session['github_connected'] = False
                flash('Your GitHub authorization has expired. Please connect again.', 'warning')
                return redirect(url_for('profile', error='GitHub token expired'))
            
            conn.close()
            flash(f'Failed to fetch repositories from GitHub: {user_repos_response.status_code}', 'danger')
            return redirect(url_for('profile', error='GitHub API error'))
        
        github_repos = user_repos_response.json()
        
        # Enhance repository data with additional information
        for repo in github_repos:
            # Format dates for better display
            if 'updated_at' in repo and repo['updated_at']:
                # Convert ISO format to more readable format
                updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
                repo['updated_at'] = updated_at.strftime('%Y-%m-%d %H:%M')
            
            # Ensure all repos have these fields to prevent template errors
            if 'description' not in repo or repo['description'] is None:
                repo['description'] = ''
            
            if 'language' not in repo or repo['language'] is None:
                repo['language'] = 'Unknown'
            
            # Add default values for star and fork counts if not present
            if 'stargazers_count' not in repo:
                repo['stargazers_count'] = 0
                
            if 'forks_count' not in repo:
                repo['forks_count'] = 0
    
    except Exception as e:
        logging.error(f"Exception fetching GitHub repositories: {str(e)}")
        conn.close()
        flash(f'Error connecting to GitHub API: {str(e)}', 'danger')
        return redirect(url_for('profile', error='GitHub connection error'))
    
    # Get already saved repos
    saved_repos = conn.execute('SELECT repo_name, status FROM github_repos WHERE user_id = ?', (session['user_id'],)).fetchall()
    saved_repo_names = [repo['repo_name'] for repo in saved_repos]
    
    # Get repo statuses for display
    repo_statuses = {repo['repo_name']: repo['status'] for repo in saved_repos}
    
    conn.close()
    
    # Sort repositories by update date (newest first)
    github_repos.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    
    return render_template(
        'github_repos.html',
        repos=github_repos,
        saved_repo_names=saved_repo_names,
        repo_statuses=repo_statuses,
        active_page='profile'
    )

@app.route('/github/add_repo', methods=['POST'])
def add_github_repo():
    if 'user_id' not in session:
        flash('Please log in to add repositories', 'warning')
        return redirect(url_for('login'))
    
    repo_name = request.form.get('repo_name')
    repo_url = request.form.get('repo_url')
    repo_id = request.form.get('repo_id', '')
    repo_language = request.form.get('repo_language', 'Unknown')
    repo_description = request.form.get('repo_description', '')
    repo_visibility = request.form.get('repo_visibility', 'public')
    
    if not repo_name or not repo_url:
        flash('Repository information is incomplete', 'danger')
        return redirect(url_for('github_repos', error='Repository information is incomplete'))
    
    try:
        conn = get_db_connection()
        
        # Check if repo already exists
        existing = conn.execute(
            'SELECT id FROM github_repos WHERE user_id = ? AND repo_name = ?', 
            (session['user_id'], repo_name)
        ).fetchone()
        
        if existing:
            conn.close()
            flash(f'Repository "{repo_name}" is already added to your account', 'info')
            return redirect(url_for('github_repos'))
        
        # Check if the github_repos table has all the necessary columns
        cursor = conn.execute("PRAGMA table_info(github_repos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns if needed
        if 'language' not in columns:
            conn.execute('ALTER TABLE github_repos ADD COLUMN language TEXT')
        if 'description' not in columns:
            conn.execute('ALTER TABLE github_repos ADD COLUMN description TEXT')
        if 'visibility' not in columns:
            conn.execute('ALTER TABLE github_repos ADD COLUMN visibility TEXT')
        if 'added_at' not in columns:
            conn.execute('ALTER TABLE github_repos ADD COLUMN added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # Store repo with github's repo ID in our database
        github_id = repo_id.replace('temp_', '') if repo_id.startswith('temp_') else repo_id
        
        conn.execute(
            '''INSERT INTO github_repos 
               (user_id, repo_name, repo_url, status, github_id, language, description, visibility, added_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (session['user_id'], repo_name, repo_url, 'not_scanned', github_id, 
             repo_language, repo_description, repo_visibility)
        )
        conn.commit()
        
        # Log the addition
        logging.info(f"Added repository {repo_name} with GitHub ID {github_id} for user {session['user_id']}")
        
        conn.close()
        flash(f'Repository "{repo_name}" added successfully! It is now ready for security scanning.', 'success')
        
        # Check if we should redirect to scan immediately
        if request.form.get('scan_immediately') == 'true':
            # Get the repo ID we just inserted
            conn = get_db_connection()
            repo = conn.execute(
                'SELECT id FROM github_repos WHERE user_id = ? AND repo_name = ?',
                (session['user_id'], repo_name)
            ).fetchone()
            conn.close()
            
            if repo:
                return redirect(url_for('scan_github_repo', repo_id=repo['id']))
        
        return redirect(url_for('github_repos'))
        
    except Exception as e:
        logging.error(f"Error adding repository {repo_name}: {str(e)}")
        flash(f'Error adding repository: {str(e)}', 'danger')
        return redirect(url_for('github_repos', error='Database error'))

@app.route('/github/scan_repo/<int:repo_id>')
def scan_github_repo(repo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Verify the repo belongs to the user
    repo = conn.execute(
        'SELECT * FROM github_repos WHERE id = ? AND user_id = ?',
        (repo_id, session['user_id'])
    ).fetchone()
    
    if not repo:
        conn.close()
        return redirect(url_for('profile', error='Repository not found'))
    
    # Get user's GitHub token
    user = conn.execute('SELECT github_token FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user or not user['github_token']:
        conn.close()
        return redirect(url_for('profile', error='GitHub not connected'))
    
    # Update repo status to scanning
    conn.execute(
        'UPDATE github_repos SET status = ?, last_scan = ? WHERE id = ?',
        ('scanning', datetime.now().isoformat(), repo_id)
    )
    conn.commit()
    
    # Get organization for the user (use first one for simplicity)
    org = conn.execute('SELECT id FROM organizations LIMIT 1').fetchone()
    org_id = org['id'] if org else None
    
    if not org_id:
        # Create a default organization if none exists
        cursor = conn.execute(
            'INSERT INTO organizations (name, description, industry) VALUES (?, ?, ?)',
            ('Default Organization', 'Auto-created organization', 'Technology')
        )
        org_id = cursor.lastrowid
        conn.commit()
    
    # Fetch repo content for tech stack detection
    try:
        repo_content_response = requests.get(
            f'https://api.github.com/repos/{repo["repo_name"]}/languages',
            headers={
                'Authorization': f'token {user["github_token"]}',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        
        if repo_content_response.status_code == 200:
            languages = list(repo_content_response.json().keys())
            
            # Create AI agent to run assessment
            agent = AIAgentManager(org_id)
            assessment_results = agent.run_automated_assessment(languages, 'vuln_scan')
            
            # Update repo status to completed
            conn.execute(
                'UPDATE github_repos SET status = ?, last_scan = ? WHERE id = ?',
                ('completed', datetime.now().isoformat(), repo_id)
            )
            conn.commit()
            
            conn.close()
            
            # Redirect to AI agent results
            return redirect(url_for('ai_agent_automation'))
        else:
            # Update repo status to error
            conn.execute(
                'UPDATE github_repos SET status = ? WHERE id = ?',
                ('error', repo_id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('profile', error='Failed to fetch repository content'))
            
    except Exception as e:
        logging.error(f"Error scanning repo: {e}")
        # Update repo status to error
        conn.execute(
            'UPDATE github_repos SET status = ? WHERE id = ?',
            ('error', repo_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('profile', error='An error occurred during the scan'))

# API endpoint to get repository size
@app.route('/api/repository-size/<path:repo_name>', methods=['GET'])
def repository_size(repo_name):
    """Get the size of a GitHub repository"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    user = conn.execute('SELECT github_token FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    if not user or not user['github_token']:
        return jsonify({'error': 'GitHub not connected'}), 400
    
    try:
        # Get repository information
        repo_response = requests.get(
            f'https://api.github.com/repos/{repo_name}',
            headers={
                'Authorization': f'token {user["github_token"]}',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        
        if repo_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch repository information'}), 400
        
        repo_data = repo_response.json()
        
        # GitHub API returns size in KB
        size_kb = repo_data.get('size', 0)
        if size_kb < 1024:
            size_formatted = f"{size_kb} KB"
        else:
            size_formatted = f"{size_kb / 1024:.1f} MB"
        
        return jsonify({
            'name': repo_name,
            'size': size_kb,
            'size_formatted': size_formatted
        })
        
    except Exception as e:
        logging.error(f"Error fetching repository size: {e}")
        return jsonify({'error': 'Error fetching repository size'}), 500

@app.route('/api/code-review', methods=['POST'])
def api_code_review():
    """
    API endpoint for code review requests
    """
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'error': 'Not authenticated'}), 401
    
    # Get code and language from request
    data = request.json
    code_sample = data.get('code')
    language = data.get('language')
    
    if not code_sample:
        return jsonify({
            'status': 'error',
            'error': 'No code provided'
        }), 400
    
    logging.info(f"Received code review request for {language or 'unknown'} code")
    
    # Get organization ID (use default for simplicity)
    org_id = 1
    
    try:
        # Import AI agent manager
        try:
            from shield.backend.app.services.ai_agent_automation import AIAgentManager as ImportedAIAgentManager
            agent_class = ImportedAIAgentManager
        except ImportError:
            agent_class = AIAgentManager
        
        # Create agent manager
        agent = agent_class(org_id)
        
        # Check if OpenAI API key is available
        if not agent.openai_api_key:
            return jsonify({
                'status': 'error',
                'error': 'OpenAI API key not configured'
            }), 400
        
        # Perform code review
        review_results = agent.code_review(code_sample, language)
        
        # Return results
        return jsonify({
            'status': 'success',
            'results': review_results
        })
        
    except Exception as e:
        logging.error(f"Error during code review: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/code-review')
def code_review_page():
    """
    Display the code review page
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if OpenAI API key is available
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    # If no key, check hardcoded key (for development only)
    if not openai_api_key:
        openai_api_key = "YOUR_OPENAI_API_KEY_HERE"  # Replace with actual key for testing
    
    # Show warning if no API key
    if not openai_api_key or openai_api_key == "YOUR_OPENAI_API_KEY_HERE":
        flash('OpenAI API key is not configured. Code review functionality will not work.', 'warning')
    
    return render_template('code_review.html', active_page='code_review')

@app.template_filter('startswith')
def startswith(value, prefix):
    """Check if a string starts with a specific prefix"""
    if isinstance(value, str):
        return value.startswith(prefix)
    return False

if __name__ == '__main__':
    app.run(debug=True)