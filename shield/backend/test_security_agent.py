"""
Test script for the security agent.
"""
import json
import os
from dotenv import load_dotenv
from app.services.agent_builder import SecurityAgent

# Load environment variables 
load_dotenv()

def test_security_agent():
    """Test the security agent with a sample tech stack."""
    # Make sure OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return False
    
    # Create a new instance of the agent
    agent = SecurityAgent()
    
    # Sample technology stack
    tech_stack = ["Python", "Flask", "SQLAlchemy", "PostgreSQL", "Docker"]
    
    print(f"Analyzing security for technology stack: {', '.join(tech_stack)}")
    print("This may take a few minutes as multiple AI calls are made...")
    
    # Run the full repository security analysis
    result = agent.analyze_repository_security(tech_stack)
    
    # Print a summary of the results
    print("\n========= SECURITY ANALYSIS RESULTS =========")
    print(f"Analyzed {len(tech_stack)} technologies")
    print(f"Found {len(result['vulnerabilities'])} potential vulnerabilities")
    
    # Print vulnerability details
    print("\n----- VULNERABILITIES -----")
    for i, vuln in enumerate(result['vulnerabilities'], 1):
        print(f"{i}. {vuln['title']} - Severity: {vuln['severity']}, CVSS: {vuln.get('cvss_score', 'N/A')}")
        print(f"   Description: {vuln['description']}")
        print(f"   Remediation: {vuln.get('remediation', 'Not specified')}")
        print()
    
    # Print risk assessment
    print("\n----- RISK ASSESSMENT -----")
    print(f"Overall Risk: {result['risk_assessment'].get('overall_risk', 'Unknown')}")
    print(f"Business Impact: {result['risk_assessment'].get('business_impact', 'Not specified')}")
    
    # Print risk factors
    print("\nRisk Factors:")
    for factor in result['risk_assessment'].get('risk_factors', ['No factors identified']):
        print(f"- {factor}")
    
    # Print recommendations
    print("\nRecommendations:")
    for rec in result['risk_assessment'].get('recommendations', ['No recommendations provided']):
        print(f"- {rec}")
    
    # Save the results to a file
    with open("security_analysis_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull results saved to security_analysis_result.json")
    
    return True

if __name__ == "__main__":
    print("Testing Security Agent...")
    try:
        success = test_security_agent()
        if success:
            print("\nSecurity agent test completed successfully.")
        else:
            print("\nSecurity agent test failed.")
    except Exception as e:
        print(f"\nError testing security agent: {str(e)}") 