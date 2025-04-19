from app.models import Vulnerability, Organization
from app.extensions import db
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os

def analyze_risk(vulnerability_id):
    """
    Analyze the business impact and risk level of a vulnerability.
    Prioritizes remediation based on business impact, resource requirements, and implementation complexity.
    
    Args:
        vulnerability_id (int): The vulnerability ID to analyze
        
    Returns:
        dict: Risk analysis results
    """
    # Get vulnerability data
    vulnerability = Vulnerability.query.get(vulnerability_id)
    if not vulnerability:
        return {'error': 'Vulnerability not found'}
    
    # Get organization data
    organization = Organization.query.get(vulnerability.organization_id)
    if not organization:
        return {'error': 'Organization not found'}
    
    # Initialize LangChain components
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.environ.get('OPENAI_API_KEY')
    )
    
    # Try to parse affected systems
    try:
        affected_systems = json.loads(vulnerability.affected_systems)
    except:
        affected_systems = []
    
    # Create a prompt template for risk analysis
    template = """
    You are a cybersecurity risk analyst evaluating the business impact of a security vulnerability.
    
    Organization Details:
    Name: {organization_name}
    Industry: {industry}
    
    Vulnerability Details:
    Title: {title}
    Description: {description}
    CVSS Score: {cvss_score}
    Severity: {severity}
    Affected Systems: {affected_systems}
    Current Status: {status}
    
    Task:
    Analyze this vulnerability from a business perspective and provide:
    1. A comprehensive business impact assessment (financial, operational, reputational)
    2. A prioritized remediation plan with clear steps
    3. Resource requirements for remediation (high/medium/low)
    4. Implementation complexity (high/medium/low)
    5. Estimated time to remediate
    
    Format your response as a JSON object with the following structure:
    {{
        "business_impact": {{
            "financial_impact": "Description of financial impact",
            "operational_impact": "Description of operational impact",
            "reputational_impact": "Description of reputational impact",
            "impact_score": 85  # 0-100 score with higher being more severe
        }},
        "remediation": {{
            "priority": "critical/high/medium/low",
            "steps": [
                "Step 1: description",
                "Step 2: description",
                ...
            ],
            "resource_requirements": "high/medium/low",
            "implementation_complexity": "high/medium/low",
            "estimated_time": "x days/weeks"
        }}
    }}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Prepare the message
    message = prompt.format(
        organization_name=organization.name,
        industry=organization.industry,
        title=vulnerability.title,
        description=vulnerability.description,
        cvss_score=vulnerability.cvss_score,
        severity=vulnerability.severity,
        affected_systems=", ".join(affected_systems) if affected_systems else "Unknown",
        status=vulnerability.status
    )
    
    # Get the response from the LLM
    response = llm.invoke(message)
    
    # Parse the response to extract risk analysis data
    try:
        # Extract JSON from the response
        response_text = response.content
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            risk_data = json.loads(json_text)
        else:
            risk_data = {
                'business_impact': {},
                'remediation': {}
            }
            
        # Update vulnerability with business impact and remediation plan
        vulnerability.business_impact = risk_data.get('business_impact', {}).get('impact_score')
        vulnerability.remediation_plan = json.dumps(risk_data.get('remediation', {}))
        db.session.commit()
        
        # Return risk analysis results
        return {
            'vulnerability_id': vulnerability_id,
            'risk_analysis': risk_data
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)} 