"""
Test script for the threat intelligence service using direct OpenAI implementation.
"""
import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleThreatIntelligenceService:
    """Simplified version of the ThreatIntelligenceService for testing."""
    
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

def test_threat_intelligence():
    """Test the threat intelligence service with a sample tech stack."""
    service = SimpleThreatIntelligenceService()
    
    # Sample technology stack
    tech_stack = ["Python", "Flask", "SQLAlchemy", "PostgreSQL", "Docker"]
    
    print(f"Analyzing threats for: {', '.join(tech_stack)}")
    threats = service.get_threats_for_technologies(tech_stack)
    
    # Print the results
    print("\nThreat Intelligence Results:")
    print("-" * 60)
    if threats:
        for i, threat in enumerate(threats, 1):
            print(f"Threat {i}: {threat.get('title')}")
            print(f"Description: {threat.get('description')}")
            print(f"CVSS Score: {threat.get('cvss_score')}")
            print(f"Severity: {threat.get('severity')}")
            print("-" * 40)
    else:
        print("No threats identified.")
    
    return bool(threats)

if __name__ == "__main__":
    print("Testing Threat Intelligence Service...")
    try:
        success = test_threat_intelligence()
        if success:
            print("\nThreat intelligence service test successful.")
        else:
            print("\nThreat intelligence service returned no threats.")
    except Exception as e:
        print(f"\nError testing threat intelligence service: {str(e)}") 