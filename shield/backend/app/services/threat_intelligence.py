from app.models import Organization, Vulnerability
from app.extensions import db
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os

def analyze_threats(org_id, tech_stack):
    """
    Analyze threat intelligence feeds and identify relevant threats based on the organization's tech stack.
    
    Args:
        org_id (int): The organization ID
        tech_stack (list): List of technologies used by the organization
        
    Returns:
        dict: Analysis results including identified threats
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
    
    # Initialize LangChain components
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.environ.get('OPENAI_API_KEY')
    )
    
    # Create a prompt template for threat analysis
    template = """
    You are a cybersecurity expert analyzing potential threats for an organization based on their technology stack.
    
    Organization: {organization_name}
    Industry: {industry}
    Technology Stack: {tech_stack}
    
    Task:
    1. Identify the top 5 most critical security vulnerabilities or threats that are relevant to this organization's tech stack
    2. For each vulnerability:
       - Provide a title and brief description
       - Assign a CVSS score (0.0-10.0)
       - Determine severity (critical, high, medium, low)
       - List affected systems within the tech stack
       - Suggest a remediation plan
    
    Format your response as a JSON object with the following structure:
    {{"threats": [
        {{
            "title": "Vulnerability Title",
            "description": "Description of the vulnerability",
            "cvss_score": 8.5,
            "severity": "high",
            "affected_systems": ["system1", "system2"],
            "remediation_plan": "Steps to remediate this vulnerability"
        }}
        // Additional vulnerabilities...
    ]}}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Prepare the message
    message = prompt.format(
        organization_name=organization.name,
        industry=organization.industry,
        tech_stack=", ".join(tech_stack)
    )
    
    # Get the response from the LLM
    response = llm.invoke(message)
    
    # Parse the response to extract threat data
    try:
        # Extract JSON from the response
        response_text = response.content
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            threat_data = json.loads(json_text)
        else:
            threat_data = {'threats': []}
            
        # Store threats in the database
        for threat in threat_data.get('threats', []):
            vulnerability = Vulnerability(
                title=threat.get('title'),
                description=threat.get('description'),
                cvss_score=threat.get('cvss_score'),
                severity=threat.get('severity'),
                affected_systems=json.dumps(threat.get('affected_systems', [])),
                remediation_plan=threat.get('remediation_plan'),
                organization_id=org_id,
                status='open'
            )
            db.session.add(vulnerability)
        
        db.session.commit()
        
        # Return the threat analysis results
        return {
            'organization_id': org_id,
            'tech_stack': tech_stack,
            'threats': threat_data.get('threats', []),
            'count': len(threat_data.get('threats', []))
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)} 