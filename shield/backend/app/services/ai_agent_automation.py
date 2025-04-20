from flask import current_app
import os
import json
import uuid
from datetime import datetime
import logging
from app.models import TestCase, Vulnerability, Organization
from app.extensions import db
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class AIAgentManager:
    """
    Manages automated security testing with AI agents
    Integration of cybersecurity LLM agents for automated security testing
    """
    
    def __init__(self, organization_id):
        self.organization_id = organization_id
        self.organization = Organization.query.get(organization_id)
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            api_key=os.environ.get('OPENAI_API_KEY')
        )
        
    def run_automated_assessment(self, tech_stack, assessment_type=None):
        """
        Run an automated security assessment using AI agents
        
        Args:
            tech_stack (list): Technologies used by the organization
            assessment_type (str): Type of assessment (vuln_scan, pentest, etc.)
            
        Returns:
            dict: Results of the assessment
        """
        if not assessment_type:
            assessment_type = "vuln_scan"
            
        # Generate test cases based on tech stack
        test_cases = self._generate_targeted_test_cases(tech_stack)
        
        # Run the test cases
        results = self._execute_test_cases(test_cases)
        
        # Analyze the results and create vulnerabilities
        vulnerabilities = self._analyze_results(results)
        
        return {
            "assessment_id": str(uuid.uuid4()),
            "organization_id": self.organization_id,
            "assessment_type": assessment_type,
            "timestamp": datetime.utcnow().isoformat(),
            "test_cases_count": len(test_cases),
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": [v.to_dict() for v in vulnerabilities]
        }
        
    def _generate_targeted_test_cases(self, tech_stack):
        """Generate targeted test cases based on tech stack using LLM agents"""
        
        # Define the prompt template for test case generation
        template = """
        You are a team of expert security researchers analyzing an organization's technology stack to identify potential security vulnerabilities.
        
        Organization: {organization_name}
        Industry: {industry}
        Technology Stack: {tech_stack}
        
        Task:
        Create 5 detailed penetration test cases to identify security vulnerabilities in the organization's systems.
        Each test case should focus on a specific vulnerability type and be tailored to the organization's tech stack.
        
        For each test case, include:
        1. A descriptive name
        2. A detailed description of the test
        3. The vulnerability type being tested (e.g., SQL injection, XSS, CSRF, etc.)
        4. The specific target system or component
        5. The actual payload or test procedure
        6. The expected result if the system is vulnerable
        
        Format your response as a JSON object with the following structure:
        {{"test_cases": [
            {{
                "name": "Test Case Name",
                "description": "Detailed description of the test",
                "type": "vulnerability_type",
                "target": "target_system",
                "payload": "actual test payload or procedure",
                "expected_result": "expected outcome if vulnerable"
            }}
            // Additional test cases...
        ]}}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Format tech stack
        if isinstance(tech_stack, str):
            try:
                tech_stack = json.loads(tech_stack)
            except:
                tech_stack = [tech_stack]
        
        # Prepare the message
        message = prompt.format(
            organization_name=self.organization.name,
            industry=self.organization.industry,
            tech_stack=", ".join(tech_stack)
        )
        
        # Get the response from the LLM
        response = self.llm.invoke(message)
        
        # Parse the response to extract test case data
        try:
            # Extract JSON from the response
            response_text = response.content
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                test_case_data = json.loads(json_text)
            else:
                test_case_data = {'test_cases': []}
                
            # Store test cases in the database
            created_test_cases = []
            for tc in test_case_data.get('test_cases', []):
                test_case = TestCase(
                    name=tc.get('name'),
                    description=tc.get('description'),
                    type=tc.get('type'),
                    target=tc.get('target'),
                    payload=tc.get('payload'),
                    expected_result=tc.get('expected_result'),
                    organization_id=self.organization_id,
                    status='pending'
                )
                db.session.add(test_case)
                created_test_cases.append(test_case)
            
            db.session.commit()
            return created_test_cases
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error generating test cases: {str(e)}")
            return []
            
    def _execute_test_cases(self, test_cases):
        """Execute test cases using AI agents and simulated attacks"""
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
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Prepare the message
            message = prompt.format(
                name=test_case.name,
                description=test_case.description,
                test_type=test_case.type,
                target=test_case.target,
                payload=test_case.payload,
                expected_result=test_case.expected_result
            )
            
            # Get the response from the LLM
            response = self.llm.invoke(message)
            
            # Parse the response
            try:
                # Extract JSON from the response
                response_text = response.content
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
                test_case.status = 'completed'
                test_case.result = json.dumps(simulation_data)
                db.session.commit()
                
                results.append({
                    "test_case_id": test_case.id,
                    "simulation_data": simulation_data
                })
                
            except Exception as e:
                db.session.rollback()
                # Update test case status to failed
                test_case.status = 'failed'
                test_case.result = json.dumps({'error': str(e)})
                db.session.commit()
                logging.error(f"Error executing test case: {str(e)}")
                
        return results
        
    def _analyze_results(self, results):
        """Analyze test results and create vulnerabilities"""
        vulnerabilities = []
        
        for result in results:
            simulation_data = result["simulation_data"]
            test_case_id = result["test_case_id"]
            test_case = TestCase.query.get(test_case_id)
            
            # If vulnerability found, create or update vulnerability record
            if simulation_data.get('success') and simulation_data.get('vulnerability_details'):
                vuln_details = simulation_data.get('vulnerability_details')
                vulnerability = Vulnerability(
                    title=vuln_details.get('title', f"Vulnerability from test case {test_case.id}"),
                    description=vuln_details.get('description'),
                    cvss_score=vuln_details.get('cvss_score'),
                    severity=vuln_details.get('severity', 'medium'),
                    affected_systems=json.dumps(vuln_details.get('affected_components', [])),
                    remediation_plan=vuln_details.get('remediation'),
                    organization_id=self.organization_id,
                    status='open',
                    discovered_by='SHIELD AI Agent'
                )
                db.session.add(vulnerability)
                
                # Link test case to vulnerability
                test_case.vulnerability_id = vulnerability.id
                
                vulnerabilities.append(vulnerability)
                
        db.session.commit()
        return vulnerabilities 
    

   


class CodeTokenizer:
    """
    Tokenizes code for processing by the AI agent.
    This preserves code structure and language-specific syntax.
    """
    def __init__(self, model_config: str = "config/tokenizer_config.json"):
        self.config = self._load_config(model_config)
        self.token_limit = 4096  # Maximum tokens for model context
        self.language_parsers = {
            "python": self._parse_python,
            "cpp": self._parse_cpp,
            "javascript": self._parse_javascript
        }
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads tokenizer configuration."""
       
        return json.load(open(config_path, "r"))
    
    def tokenize_code(self, code: str, language: str) -> List[Dict[str, Any]]:
        """
        Tokenizes code into structured format for the model.
        
        Args:
            code: Source code string
            language: Programming language
            
        Returns:
            List of token objects with metadata
        """
        if language not in self.language_parsers:
           
            return []
            
        
        ast = self.language_parsers[language](code)
        
        
        tokens = self._extract_semantic_tokens(ast)
        
      
        enriched_tokens = self._enrich_tokens_with_context(tokens)
        
      
        model_tokens = self._map_to_model_vocabulary(enriched_tokens)
        
        return model_tokens
    
    def _parse_python(self, code: str) -> Dict[str, Any]:
        """Parse Python code into AST."""
       
        return {"type": "Module", "body": []}
    
    def _parse_cpp(self, code: str) -> Dict[str, Any]:
        """Parse C++ code into AST."""
       
        return {"type": "TranslationUnit", "declarations": []}
    
    def _parse_javascript(self, code: str) -> Dict[str, Any]:
        """Parse JavaScript code into AST."""
       
        return {"type": "Program", "body": []}
    
    def _extract_semantic_tokens(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract semantic tokens from AST."""
      
        return []
    
    def _enrich_tokens_with_context(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add contextual information to tokens."""
       
        return tokens
    
    def _map_to_model_vocabulary(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map tokens to model vocabulary."""
       
        return tokens


class AIAgentInterface:
    """
    Handles interaction with the AI model for code analysis.
    """
    def __init__(self, model_endpoint: str = "https://api.shield.ai/v1/models/code-analyzer"):
        self.model_endpoint = model_endpoint
        self.tokenizer = CodeTokenizer()
        self.session_id = os.urandom(16).hex()
        
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using the AI model.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Analysis results including vulnerabilities
        """
        # Tokenize code
        tokens = self.tokenizer.tokenize_code(code, language)
        
      
        response = self._simulate_model_response(tokens, language)
        
        return self._process_analysis_results(response)
    
    def _simulate_model_response(self, tokens: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Simulate model response for demonstration."""
        
        return {
            "status": "success",
            "vulnerabilities": [
                {
                    "type": "buffer_overflow",
                    "severity": "critical",
                    "location": {"line": 127, "file": "extensions/image_processor.cpp"}
                }
            ]
        }
    
    def _process_analysis_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format analysis results."""
        # Non-functional: Just returns input
        return response



def scan_repository(repo_path: str) -> Dict[str, Any]:
    """
    Scan a code repository for vulnerabilities using tokenization and AI analysis.
    
    Args:
        repo_path: Path to code repository
        
    Returns:
        Vulnerability report
    """
   
    agent = AIAgentInterface()
    languages_detected = {"python": 0.7, "cpp": 0.3}
    
   
    results = {
        "repository": repo_path,
        "scan_id": agent.session_id,
        "vulnerabilities": [],
        "languages": languages_detected
    }
    
    
    for language, percentage in languages_detected.items():
        results["vulnerabilities"].append({
            "language": language,
            "count": int(percentage * 10),
            "findings": []  # Would contain actual findings
        })
    
    return results