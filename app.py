from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import json
import uuid
from datetime import datetime
import sqlite3
import logging
import requests
from urllib.parse import urlencode
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)

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
    def __init__(self, organization_id):
        self.organization_id = organization_id
        conn = get_db_connection()
        org = conn.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,)).fetchone()
        self.organization = dict(org)
        conn.close()
    
    def run_automated_assessment(self, tech_stack, assessment_type=None):
        """Generate test cases and simulate attacks using AI"""
        if not assessment_type:
            assessment_type = "vuln_scan"
        
        # Generate test cases
        test_cases = self._generate_targeted_test_cases(tech_stack)
        
        # Execute test cases
        results = self._execute_test_cases(test_cases)
        
        # Analyze results and create vulnerabilities
        vulnerabilities = self._analyze_results(results)
        
        # Return assessment results
        return {
            "assessment_id": str(uuid.uuid4()),
            "organization_id": self.organization_id,
            "assessment_type": assessment_type,
            "timestamp": datetime.now().isoformat(),
            "test_cases_count": len(test_cases),
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities
        }
    
    def _generate_targeted_test_cases(self, tech_stack):
        """Generate test cases based on tech stack"""
        # Parse tech stack
        if isinstance(tech_stack, str):
            try:
                tech_stack = json.loads(tech_stack)
            except:
                tech_stack = [tech_stack]
        
        conn = get_db_connection()
        created_test_cases = []
        
        # Sample test cases based on common web vulnerabilities
        sample_test_cases = [
            {
                "name": f"SQL Injection Test for {tech}",
                "description": f"Test for SQL injection vulnerabilities in {tech} applications",
                "type": "sql_injection",
                "target": f"{tech} database interface",
                "payload": "' OR 1=1 --",
                "expected_result": "Database returns all records instead of specific ones"
            } for tech in tech_stack if tech.lower() in ['mysql', 'postgresql', 'sql server', 'sqlite', 'django', 'flask', 'spring']
        ]
        
        # Add XSS test cases for web technologies
        sample_test_cases.extend([
            {
                "name": f"Cross-Site Scripting (XSS) Test for {tech}",
                "description": f"Test for XSS vulnerabilities in {tech} frontend",
                "type": "xss",
                "target": f"{tech} user input fields",
                "payload": "<script>alert('XSS')</script>",
                "expected_result": "Script executes in the browser context"
            } for tech in tech_stack if tech.lower() in ['javascript', 'react', 'angular', 'vue.js', 'html', 'jquery']
        ])
        
        # Add CSRF test cases
        sample_test_cases.extend([
            {
                "name": f"CSRF Protection Test for {tech}",
                "description": f"Test for CSRF vulnerabilities in {tech} applications",
                "type": "csrf",
                "target": f"{tech} form submissions",
                "payload": "Forge a form submission without CSRF token",
                "expected_result": "Server accepts the request without validation"
            } for tech in tech_stack if tech.lower() in ['django', 'flask', 'spring', 'express', 'php']
        ])
        
        # Add more test cases as needed
        if not sample_test_cases:
            # Fallback test cases if no matching technologies
            sample_test_cases = [
                {
                    "name": "Generic SQL Injection Test",
                    "description": "Basic SQL injection test for web applications",
                    "type": "sql_injection",
                    "target": "Web application database interface",
                    "payload": "' OR 1=1 --",
                    "expected_result": "Database returns all records"
                },
                {
                    "name": "Generic XSS Test",
                    "description": "Basic XSS test for web applications",
                    "type": "xss",
                    "target": "Web application user inputs",
                    "payload": "<script>alert('XSS')</script>",
                    "expected_result": "Script executes in browser"
                }
            ]
        
        # Store test cases in database
        for tc in sample_test_cases:
            cursor = conn.execute('''
            INSERT INTO test_cases (name, description, type, target, payload, expected_result, status, organization_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tc["name"],
                tc["description"],
                tc["type"],
                tc["target"],
                tc["payload"],
                tc["expected_result"],
                "pending",
                self.organization_id
            ))
            conn.commit()
            
            # Get the inserted test case
            test_case = conn.execute("SELECT * FROM test_cases WHERE id = ?", (cursor.lastrowid,)).fetchone()
            created_test_cases.append(dict(test_case))
        
        conn.close()
        return created_test_cases
    
    def _execute_test_cases(self, test_cases):
        """Simulate running test cases"""
        results = []
        conn = get_db_connection()
        
        for test_case in test_cases:
            # Simulate test execution
            is_vulnerable = test_case['type'] in ['sql_injection', 'xss', 'csrf']
            simulation_data = self._generate_simulation_data(test_case, is_vulnerable)
            
            # Update test case status
            conn.execute('''
            UPDATE test_cases
            SET status = ?, result = ?
            WHERE id = ?
            ''', ('completed', json.dumps(simulation_data), test_case['id']))
            conn.commit()
            
            results.append({
                "test_case_id": test_case['id'],
                "simulation_data": simulation_data
            })
        
        conn.close()
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

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Basic authentication for demo purposes
        if username == 'admin' and password == 'password':
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    organizations = conn.execute('SELECT * FROM organizations').fetchall()
    
    # Get organization ID from query params or use first one
    org_id = request.args.get('organization_id', type=int)
    if not org_id and organizations:
        org_id = organizations[0]['id']
    
    # Fetch stats for selected organization
    vuln_stats = {}
    test_case_stats = {}
    recent_vulns = []
    
    if org_id:
        # Vulnerability stats by severity
        severities = ['critical', 'high', 'medium', 'low']
        for severity in severities:
            count = conn.execute(
                'SELECT COUNT(*) FROM vulnerabilities WHERE organization_id = ? AND severity = ?', 
                (org_id, severity)
            ).fetchone()[0]
            vuln_stats[severity] = count
        
        # Ensure we have a total count that's not zero for division operations
        total_test_cases = conn.execute('SELECT COUNT(*) FROM test_cases WHERE organization_id = ?', (org_id,)).fetchone()[0]
        test_case_stats = {
            'total': total_test_cases,
            'pending': conn.execute('SELECT COUNT(*) FROM test_cases WHERE organization_id = ? AND status = ?', (org_id, 'pending')).fetchone()[0],
            'running': conn.execute('SELECT COUNT(*) FROM test_cases WHERE organization_id = ? AND status = ?', (org_id, 'running')).fetchone()[0],
            'completed': conn.execute('SELECT COUNT(*) FROM test_cases WHERE organization_id = ? AND status = ?', (org_id, 'completed')).fetchone()[0],
            'failed': conn.execute('SELECT COUNT(*) FROM test_cases WHERE organization_id = ? AND status = ?', (org_id, 'failed')).fetchone()[0],
        }
        
        # Ensure there's always a non-zero value for the total to prevent division by zero
        if test_case_stats['total'] == 0:
            test_case_stats['total'] = 1
        
        # Recent vulnerabilities
        recent_vulns = conn.execute(
            'SELECT * FROM vulnerabilities WHERE organization_id = ? ORDER BY discovered_at DESC LIMIT 5', 
            (org_id,)
        ).fetchall()
    
    conn.close()
    
    return render_template(
        'dashboard.html', 
        organizations=organizations,
        vuln_stats=vuln_stats,
        test_case_stats=test_case_stats,
        recent_vulnerabilities=recent_vulns,
        active_page='dashboard'
    )

@app.route('/organizations')
def organizations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    organizations = conn.execute('SELECT * FROM organizations').fetchall()
    conn.close()
    
    return render_template('organizations.html', organizations=organizations, active_page='organizations')

@app.route('/vulnerabilities')
def vulnerabilities():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    org_id = request.args.get('organization_id', type=int)
    
    conn = get_db_connection()
    
    # Fetch all organizations
    organizations = conn.execute('SELECT * FROM organizations').fetchall()
    
    # If no org_id specified, use the first organization
    if not org_id and organizations:
        org_id = organizations[0]['id']
    
    # Fetch vulnerabilities for the selected organization
    vulnerabilities = []
    if org_id:
        vulnerabilities = conn.execute(
            'SELECT * FROM vulnerabilities WHERE organization_id = ? ORDER BY discovered_at DESC', 
            (org_id,)
        ).fetchall()
    
    conn.close()
    
    return render_template(
        'vulnerabilities.html', 
        vulnerabilities=vulnerabilities,
        organizations=organizations,
        selected_org=org_id,
        active_page='vulnerabilities'
    )

@app.route('/test-cases')
def test_cases():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    org_id = request.args.get('organization_id', type=int)
    
    conn = get_db_connection()
    
    # Fetch all organizations
    organizations = conn.execute('SELECT * FROM organizations').fetchall()
    
    # If no org_id specified, use the first organization
    if not org_id and organizations:
        org_id = organizations[0]['id']
    
    # Fetch test cases for the selected organization
    test_cases = []
    if org_id:
        test_cases = conn.execute(
            'SELECT * FROM test_cases WHERE organization_id = ? ORDER BY created_at DESC', 
            (org_id,)
        ).fetchall()
    
    conn.close()
    
    return render_template(
        'test_cases.html', 
        test_cases=test_cases,
        organizations=organizations,
        selected_org=org_id,
        active_page='test_cases'
    )

@app.route('/ai-agent-automation', methods=['GET', 'POST'])
def ai_agent_automation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    organizations = conn.execute('SELECT * FROM organizations').fetchall()
    
    # Default to first organization
    selected_org = organizations[0] if organizations else None
    org_id = selected_org['id'] if selected_org else None
    
    # Parse tech stack for the selected organization
    tech_stack = []
    if selected_org and selected_org['tech_stack']:
        try:
            tech_stack = json.loads(selected_org['tech_stack'])
        except:
            tech_stack = []
    
    # Fetch existing test cases and vulnerabilities
    test_cases = []
    vulnerabilities = []
    assessment_results = None
    
    if org_id:
        test_cases = conn.execute(
            'SELECT * FROM test_cases WHERE organization_id = ? ORDER BY created_at DESC', 
            (org_id,)
        ).fetchall()
        
        vulnerabilities = conn.execute(
            'SELECT * FROM vulnerabilities WHERE organization_id = ? AND discovered_by = ? ORDER BY discovered_at DESC', 
            (org_id, 'SHIELD AI Agent')
        ).fetchall()
    
    # Handle form submission
    if request.method == 'POST':
        org_id = request.form.get('organization_id', type=int)
        assessment_type = request.form.get('assessment_type', 'vuln_scan')
        tech_input = request.form.get('tech_stack', '')
        
        # Parse tech stack from form
        if tech_input:
            tech_stack = [tech.strip() for tech in tech_input.split(',')]
        
        # Run assessment
        if org_id and tech_stack:
            agent = AIAgentManager(org_id)
            assessment_results = agent.run_automated_assessment(tech_stack, assessment_type)
            
            # Refresh test cases and vulnerabilities
            test_cases = conn.execute(
                'SELECT * FROM test_cases WHERE organization_id = ? ORDER BY created_at DESC', 
                (org_id,)
            ).fetchall()
            
            vulnerabilities = conn.execute(
                'SELECT * FROM vulnerabilities WHERE organization_id = ? AND discovered_by = ? ORDER BY discovered_at DESC', 
                (org_id, 'SHIELD AI Agent')
            ).fetchall()
    
    conn.close()
    
    return render_template(
        'ai_agent_automation.html',
        organizations=organizations,
        selected_org=org_id,
        test_cases=test_cases,
        vulnerabilities=vulnerabilities,
        tech_stack=tech_stack,
        assessment_results=assessment_results,
        active_page='ai_agent_automation'
    )

@app.route('/test-cases/<int:test_case_id>')
def test_case_detail(test_case_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    test_case = conn.execute('SELECT * FROM test_cases WHERE id = ?', (test_case_id,)).fetchone()
    
    # Get organization
    organization = None
    if test_case and test_case['organization_id']:
        organization = conn.execute(
            'SELECT * FROM organizations WHERE id = ?', 
            (test_case['organization_id'],)
        ).fetchone()
    
    # Get vulnerability if linked
    vulnerability = None
    if test_case and test_case['vulnerability_id']:
        vulnerability = conn.execute(
            'SELECT * FROM vulnerabilities WHERE id = ?', 
            (test_case['vulnerability_id'],)
        ).fetchone()
    
    conn.close()
    
    if not test_case:
        return redirect(url_for('test_cases'))
    
    # Parse result if available
    result = None
    if test_case['result']:
        try:
            result = json.loads(test_case['result'])
        except:
            result = None
    
    return render_template(
        'test_case_detail.html',
        test_case=test_case,
        organization=organization,
        vulnerability=vulnerability,
        result=result,
        active_page='test_cases'
    )

@app.route('/vulnerabilities/<int:vulnerability_id>')
def vulnerability_detail(vulnerability_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    vulnerability = conn.execute('SELECT * FROM vulnerabilities WHERE id = ?', (vulnerability_id,)).fetchone()
    
    # Get organization
    organization = None
    if vulnerability and vulnerability['organization_id']:
        organization = conn.execute(
            'SELECT * FROM organizations WHERE id = ?', 
            (vulnerability['organization_id'],)
        ).fetchone()
    
    # Get linked test cases
    test_cases = []
    if vulnerability:
        test_cases = conn.execute(
            'SELECT * FROM test_cases WHERE vulnerability_id = ?', 
            (vulnerability_id,)
        ).fetchall()
    
    conn.close()
    
    if not vulnerability:
        return redirect(url_for('vulnerabilities'))
    
    # Parse affected systems if available
    affected_systems = []
    if vulnerability['affected_systems']:
        try:
            affected_systems = json.loads(vulnerability['affected_systems'])
        except:
            affected_systems = []
    
    return render_template(
        'vulnerability_detail.html',
        vulnerability=vulnerability,
        organization=organization,
        test_cases=test_cases,
        affected_systems=affected_systems,
        active_page='vulnerabilities'
    )

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
        return redirect(url_for('login'))
    
    # Generate a random state parameter to prevent CSRF attacks
    state = secrets.token_hex(16)
    session['github_oauth_state'] = state
    
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verify state parameter to prevent CSRF attacks
    if 'github_oauth_state' not in session or session['github_oauth_state'] != request.args.get('state'):
        return redirect(url_for('profile', error='Invalid state parameter'))
    
    # Exchange the code for an access token
    code = request.args.get('code')
    if not code:
        return redirect(url_for('profile', error='Authorization code not received'))
    
    # Request the access token
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GITHUB_CALLBACK_URL
        },
        headers={'Accept': 'application/json'}
    )
    
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    
    if not access_token:
        return redirect(url_for('profile', error='Failed to obtain access token'))
    
    # Store the token in the database
    conn = get_db_connection()
    conn.execute('UPDATE users SET github_token = ? WHERE id = ?', (access_token, session['user_id']))
    conn.commit()
    conn.close()
    
    # Redirect to fetch repos page
    return redirect(url_for('github_repos'))

@app.route('/github/repos')
def github_repos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user or not user['github_token']:
        conn.close()
        return redirect(url_for('profile', error='GitHub not connected'))
    
    # Fetch repositories from GitHub
    user_repos_response = requests.get(
        'https://api.github.com/user/repos',
        headers={
            'Authorization': f'token {user["github_token"]}',
            'Accept': 'application/vnd.github.v3+json'
        }
    )
    
    if user_repos_response.status_code != 200:
        conn.close()
        return redirect(url_for('profile', error='Failed to fetch repositories from GitHub'))
    
    github_repos = user_repos_response.json()
    
    # Get already saved repos
    saved_repos = conn.execute('SELECT repo_name FROM github_repos WHERE user_id = ?', (session['user_id'],)).fetchall()
    saved_repo_names = [repo['repo_name'] for repo in saved_repos]
    
    conn.close()
    
    return render_template(
        'github_repos.html',
        repos=github_repos,
        saved_repo_names=saved_repo_names,
        active_page='profile'
    )

@app.route('/github/add_repo', methods=['POST'])
def add_github_repo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    repo_name = request.form.get('repo_name')
    repo_url = request.form.get('repo_url')
    
    if not repo_name or not repo_url:
        return redirect(url_for('github_repos', error='Repository information is incomplete'))
    
    conn = get_db_connection()
    
    # Check if repo already exists
    existing = conn.execute(
        'SELECT id FROM github_repos WHERE user_id = ? AND repo_name = ?', 
        (session['user_id'], repo_name)
    ).fetchone()
    
    if not existing:
        conn.execute(
            'INSERT INTO github_repos (user_id, repo_name, repo_url, status) VALUES (?, ?, ?, ?)',
            (session['user_id'], repo_name, repo_url, 'not_scanned')
        )
        conn.commit()
    
    conn.close()
    return redirect(url_for('profile'))

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

if __name__ == '__main__':
    app.run(debug=True) 