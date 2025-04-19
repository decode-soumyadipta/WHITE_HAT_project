from app.models import Organization, Vulnerability
from app.extensions import db
import openai
import json
import os

class ThreatIntelligenceService:
    """Service for gathering and analyzing threat intelligence data."""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Configure OpenAI
        openai.api_key = self.api_key
        
    def get_threats_for_technologies(self, technologies):
        """Get threat intelligence for specific technologies."""
        tech_list = ", ".join(technologies) if isinstance(technologies, list) else technologies
        
        # Create a prompt for the language model
        prompt = f"""
        You are a cybersecurity expert. Provide information about the top 3 most critical 
        security vulnerabilities or threats for the following technologies:
        
        {tech_list}
        
        For each vulnerability:
        - Title
        - Brief description
        - CVSS score (0.0-10.0)
        - Severity (critical, high, medium, low)
        
        Format as JSON with an array of threats.
        """
        
        try:
            # Use OpenAI Completion API directly
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1000,
                temperature=0,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract content from response
            response_text = response.choices[0].text.strip()
            
            # Parse JSON data from response
            try:
                # Check if response is already JSON formatted
                data = json.loads(response_text)
                return data.get('threats', [])
            except json.JSONDecodeError:
                # If not JSON, extract JSON portion if possible
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    try:
                        data = json.loads(json_text)
                        return data.get('threats', [])
                    except:
                        pass
                
                # Return simplified format if JSON parsing fails
                return [{
                    "title": "Manual security assessment required",
                    "description": "The system was unable to automatically detect specific threats. A manual security assessment is recommended.",
                    "cvss_score": 5.0,
                    "severity": "medium"
                }]
        except Exception as e:
            # Handle API errors gracefully
            print(f"OpenAI API error: {str(e)}")
            return [{
                "title": "API Error",
                "description": f"Error connecting to threat intelligence service: {str(e)}",
                "cvss_score": 5.0,
                "severity": "medium"
            }]
    
    def analyze_organization_threats(self, org_id):
        """Analyze threats for a specific organization based on their tech stack."""
        organization = Organization.query.get(org_id)
        if not organization:
            return {'error': 'Organization not found'}
        
        # Get tech stack from organization
        try:
            tech_stack = json.loads(organization.tech_stack) if organization.tech_stack else []
        except:
            tech_stack = []
        
        if not tech_stack:
            return {'warning': 'No technology stack defined for this organization'}
        
        # Create a prompt for the organization analysis
        prompt = f"""
        You are a cybersecurity expert analyzing potential threats for an organization.
        
        Organization: {organization.name}
        Industry: {organization.industry}
        Technology Stack: {', '.join(tech_stack)}
        
        Identify the top 5 critical security vulnerabilities relevant to this organization.
        For each vulnerability:
        - Title and brief description
        - CVSS score (0.0-10.0)
        - Severity level
        - Affected systems
        - Remediation plan
        
        Format as JSON with an array of threats.
        """
        
        try:
            # Use OpenAI Completion API directly
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1500,
                temperature=0,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract content from response
            response_text = response.choices[0].text.strip()
            
            # Parse the response
            try:
                # Try to extract JSON from the response
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
                
                return {
                    'organization_id': org_id,
                    'tech_stack': tech_stack,
                    'threats': threat_data.get('threats', []),
                    'count': len(threat_data.get('threats', []))
                }
                
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}
        except Exception as e:
            return {'error': f"OpenAI API error: {str(e)}"}

# Legacy function kept for compatibility
def analyze_threats(org_id, tech_stack):
    service = ThreatIntelligenceService()
    return service.analyze_organization_threats(org_id) 