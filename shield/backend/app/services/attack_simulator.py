from app.models import TestCase, Vulnerability
from app.extensions import db
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os
import time
import random

def simulate_attacks(test_case_id):
    """
    Simulate an attack based on the specified test case.
    This is a sandbox simulation that doesn't actually attack real systems.
    
    Args:
        test_case_id (int): The test case ID to simulate
        
    Returns:
        dict: Simulation results
    """
    # Get test case data
    test_case = TestCase.query.get(test_case_id)
    if not test_case:
        return {'error': 'Test case not found'}
    
    # Update test case status to running
    test_case.status = 'running'
    db.session.commit()
    
    # Initialize LangChain components
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.2,  # Small amount of randomness for realistic simulation
        api_key=os.environ.get('OPENAI_API_KEY')
    )
    
    # Create a prompt template for attack simulation
    template = """
    You are a cybersecurity expert simulating an attack in a sandbox environment.
    
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
    
    # Simulate processing time
    time.sleep(1)
    
    # Get the response from the LLM
    response = llm.invoke(message)
    
    # Parse the response to extract simulation data
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
                organization_id=test_case.organization_id,
                status='open',
                discovered_by='SHIELD Attack Simulator'
            )
            db.session.add(vulnerability)
            
            # Link test case to vulnerability
            test_case.vulnerability_id = vulnerability.id
        
        db.session.commit()
        
        # Return simulation results
        return {
            'test_case_id': test_case_id,
            'status': 'completed',
            'simulation_results': simulation_data
        }
        
    except Exception as e:
        db.session.rollback()
        # Update test case status to failed
        test_case.status = 'failed'
        test_case.result = json.dumps({'error': str(e)})
        db.session.commit()
        return {'error': str(e)} 