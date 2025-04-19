"""
Standalone script to test the security agent implementation.
"""
import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Make sure OpenAI API key is set
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. "
                      "Please set it in your .env file or environment variables.")

# Define a simple security analysis agent
class SimpleSecurityAgent:
    """Simple security analysis agent using OpenAI."""
    
    def __init__(self):
        """Initialize the agent with OpenAI API key."""
        import openai
        self.openai = openai
        self.openai.api_key = api_key
    
    def analyze_technologies(self, technologies):
        """Analyze a list of technologies for security vulnerabilities."""
        # Convert technologies to string
        tech_list = ", ".join(technologies) if isinstance(technologies, list) else technologies
        
        # Create the prompt
        prompt = f"""
        As a cybersecurity expert, analyze the following technology stack for security vulnerabilities:
        
        Technology Stack: {tech_list}
        
        Provide:
        1. The top 3 most critical security vulnerabilities that could affect this stack
        2. The CVSS score and severity for each vulnerability
        3. Recommended security controls or mitigations
        
        Format your response as JSON with the following structure:
        {{
            "vulnerabilities": [
                {{
                    "title": "Vulnerability Title",
                    "description": "Description of the vulnerability",
                    "cvss_score": 8.5,
                    "severity": "high",
                    "affected_components": ["component1", "component2"],
                    "mitigation": "Steps to mitigate this vulnerability"
                }}
            ],
            "overall_risk": "High/Medium/Low",
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }}
        """
        
        try:
            # Call OpenAI API
            response = self.openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1500,
                temperature=0.2,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Get the response text
            response_text = response.choices[0].text.strip()
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    analysis = json.loads(json_text)
                    return analysis
                else:
                    logger.warning("Could not extract JSON from response")
                    return {
                        "error": "Could not extract JSON from response",
                        "raw_response": response_text
                    }
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                return {
                    "error": f"JSON parsing error: {str(e)}",
                    "raw_response": response_text
                }
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "error": f"OpenAI API error: {str(e)}"
            }

def run_test():
    """Run a test of the security agent."""
    # Sample tech stack to analyze
    tech_stack = ["Python", "Flask", "SQLAlchemy", "PostgreSQL", "Docker"]
    
    logger.info(f"Testing security analysis for: {', '.join(tech_stack)}")
    
    # Create the agent
    agent = SimpleSecurityAgent()
    
    # Analyze the tech stack
    logger.info("Starting security analysis...")
    result = agent.analyze_technologies(tech_stack)
    
    # Check if there was an error
    if "error" in result:
        logger.error(f"Error in security analysis: {result['error']}")
        if "raw_response" in result:
            logger.debug(f"Raw response: {result['raw_response']}")
        return False
    
    # Print the results
    logger.info("Security Analysis Results:")
    logger.info(f"Overall Risk: {result.get('overall_risk', 'Not specified')}")
    
    vulnerabilities = result.get("vulnerabilities", [])
    logger.info(f"Found {len(vulnerabilities)} vulnerabilities:")
    
    for i, vuln in enumerate(vulnerabilities, 1):
        logger.info(f"Vulnerability {i}: {vuln.get('title', 'Unknown')}")
        logger.info(f"  Severity: {vuln.get('severity', 'Unknown')}")
        logger.info(f"  CVSS Score: {vuln.get('cvss_score', 'Unknown')}")
        logger.info(f"  Description: {vuln.get('description', 'No description')}")
        if "mitigation" in vuln:
            logger.info(f"  Mitigation: {vuln.get('mitigation')}")
        logger.info("")
    
    # Print recommendations
    recommendations = result.get("recommendations", [])
    logger.info(f"Recommendations ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        logger.info(f"  {i}. {rec}")
    
    # Save the results to a file
    output_file = "security_analysis_result.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    logger.info(f"Results saved to {output_file}")
    
    return True

if __name__ == "__main__":
    logger.info("Starting standalone security agent test")
    success = run_test()
    if success:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed") 