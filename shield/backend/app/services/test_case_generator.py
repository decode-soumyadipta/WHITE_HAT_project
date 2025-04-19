from app.models import Organization, TestCase
from app.extensions import db
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os

def generate_test_cases(org_id, tech_stack, vulnerability_types=None):
    """
    Generate security test cases based on the organization's technology stack and targeted vulnerability types.
    
    Args:
        org_id (int): The organization ID
        tech_stack (list): List of technologies used by the organization
        vulnerability_types (list, optional): Types of vulnerabilities to focus on
        
    Returns:
        dict: Generated test cases and metadata
    """
    # Get organization data
    organization = Organization.query.get(org_id)
    if not organization:
        return {'error': 'Organization not found'}
    
    # Prepare the tech stack for analysis
    if isinstance(tech_stack, str):
        try:
            tech_stack = json.loads(tech_stack)
        except:
            tech_stack = [tech_stack]
    
    # Default vulnerability types if none provided
    if not vulnerability_types:
        vulnerability_types = [
            "sql_injection", 
            "xss", 
            "csrf", 
            "broken_authentication", 
            "sensitive_data_exposure"
        ]
    
    # Initialize LangChain components
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.environ.get('OPENAI_API_KEY')
    )
    
    # Create a prompt template for test case generation
    template = """
    You are a cybersecurity expert creating penetration test cases for an organization based on their technology stack.
    
    Organization: {organization_name}
    Industry: {industry}
    Technology Stack: {tech_stack}
    Vulnerability Types to Test: {vulnerability_types}
    
    Task:
    Create 5 detailed penetration test cases to identify security vulnerabilities in the organization's systems.
    Each test case should be focused on one of the specified vulnerability types and tailored to the organization's tech stack.
    
    For each test case, include:
    1. A descriptive name
    2. A detailed description of the test
    3. The vulnerability type being tested
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
    
    # Prepare the message
    message = prompt.format(
        organization_name=organization.name,
        industry=organization.industry,
        tech_stack=", ".join(tech_stack),
        vulnerability_types=", ".join(vulnerability_types)
    )
    
    # Get the response from the LLM
    response = llm.invoke(message)
    
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
        for tc in test_case_data.get('test_cases', []):
            test_case = TestCase(
                name=tc.get('name'),
                description=tc.get('description'),
                type=tc.get('type'),
                target=tc.get('target'),
                payload=tc.get('payload'),
                expected_result=tc.get('expected_result'),
                organization_id=org_id,
                status='pending'
            )
            db.session.add(test_case)
        
        db.session.commit()
        
        # Return the generated test cases
        return {
            'organization_id': org_id,
            'tech_stack': tech_stack,
            'vulnerability_types': vulnerability_types,
            'test_cases': test_case_data.get('test_cases', []),
            'count': len(test_case_data.get('test_cases', []))
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)} 