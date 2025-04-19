"""
Agent builder service for security analysis.
"""
import os
import json
import logging
import openai
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SecurityAgent:
    """Security agent using OpenAI for threat analysis and vulnerability detection."""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Configure OpenAI
        openai.api_key = self.api_key
        
        # Set the default model
        self.model = "text-davinci-003"  # You can use "gpt-3.5-turbo" if using ChatCompletions
        
        # Agent state for conversation memory
        self.conversation_history = []
    
    def _call_llm(self, prompt, max_tokens=1000):
        """Call the language model with the given prompt."""
        try:
            response = openai.Completion.create(
                engine=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.2,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            return f"Error: {str(e)}"
    
    def analyze_technologies(self, tech_stack):
        """Analyze security vulnerabilities for the given technology stack."""
        # Convert tech_stack to string if it's a list
        if isinstance(tech_stack, list):
            tech_list = ", ".join(tech_stack)
        else:
            tech_list = tech_stack
        
        # Construct the prompt
        prompt = f"""
        You are a cybersecurity expert tasked with analyzing security vulnerabilities.
        
        Technology Stack: {tech_list}
        
        Please analyze this technology stack and provide:
        1. The top 3 critical security vulnerabilities that could affect this stack
        2. Recommended security test cases for each vulnerability
        3. Remediation steps to address each vulnerability
        
        Format your response as JSON with the following structure:
        {{
            "vulnerabilities": [
                {{
                    "title": "Vulnerability Title",
                    "description": "Description of the vulnerability",
                    "cvss_score": 8.5,
                    "severity": "high",
                    "affected_components": ["component1", "component2"],
                    "test_cases": ["Test case 1", "Test case 2"],
                    "remediation": "Steps to fix this vulnerability"
                }}
            ]
        }}
        """
        
        # Add to conversation history
        self.conversation_history.append(("system", prompt))
        
        # Call the language model
        response = self._call_llm(prompt, max_tokens=1500)
        
        # Add the response to conversation history
        self.conversation_history.append(("assistant", response))
        
        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response[json_start:json_end]
                result = json.loads(json_text)
                return result
            else:
                logger.warning("No valid JSON found in response")
                return {
                    "vulnerabilities": [{
                        "title": "Analysis Error",
                        "description": "The system was unable to provide a structured analysis. Please try again.",
                        "cvss_score": 5.0,
                        "severity": "medium",
                        "affected_components": ["unknown"],
                        "test_cases": ["Manual review required"],
                        "remediation": "Consult with a security expert"
                    }]
                }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return {
                "error": "Could not parse response as JSON",
                "raw_response": response
            }
    
    def generate_test_cases(self, vulnerability):
        """Generate specific test cases for a vulnerability."""
        prompt = f"""
        You are a security testing expert. Generate detailed test cases for the following vulnerability:
        
        Vulnerability: {vulnerability['title']}
        Description: {vulnerability['description']}
        Severity: {vulnerability['severity']}
        
        Provide 3 specific, actionable test cases that could identify this vulnerability.
        Format your response as a JSON array of test case objects with the following structure:
        [
            {{
                "name": "Test Case Name",
                "description": "Detailed description of the test case",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "expected_result": "What to expect if the vulnerability exists",
                "remediation": "How to fix the issue if found"
            }}
        ]
        """
        
        # Call the language model
        response = self._call_llm(prompt, max_tokens=1000)
        
        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response[json_start:json_end]
                return json.loads(json_text)
            else:
                logger.warning("No valid JSON array found in response")
                return [{
                    "name": "Manual Testing Required",
                    "description": "The system was unable to generate specific test cases.",
                    "steps": ["Consult with a security expert"],
                    "expected_result": "N/A",
                    "remediation": "Manual assessment needed"
                }]
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return [{
                "name": "Error Generating Test Cases",
                "description": f"Error: {str(e)}",
                "steps": ["Review the vulnerability manually"],
                "expected_result": "N/A",
                "remediation": "N/A"
            }]
    
    def assess_risk(self, tech_stack, vulnerabilities):
        """Assess the overall risk based on the technology stack and identified vulnerabilities."""
        # Convert tech_stack to string if it's a list
        if isinstance(tech_stack, list):
            tech_list = ", ".join(tech_stack)
        else:
            tech_list = tech_stack
        
        # Construct the vulnerability summary
        vuln_summary = ""
        for i, vuln in enumerate(vulnerabilities, 1):
            vuln_summary += f"{i}. {vuln['title']} (Severity: {vuln['severity']}, CVSS: {vuln['cvss_score']})\n"
        
        # Construct the prompt
        prompt = f"""
        You are a risk assessment expert. Assess the overall security risk for an organization with the following:
        
        Technology Stack: {tech_list}
        
        Identified Vulnerabilities:
        {vuln_summary}
        
        Provide a comprehensive risk assessment including:
        1. Overall risk rating (Critical, High, Medium, Low)
        2. Potential business impact
        3. Key risk factors
        4. Recommendations for risk mitigation
        
        Format your response as JSON with the following structure:
        {{
            "overall_risk": "High",
            "business_impact": "Description of potential business impact",
            "risk_factors": ["Factor 1", "Factor 2", "Factor 3"],
            "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
        }}
        """
        
        # Call the language model
        response = self._call_llm(prompt, max_tokens=1000)
        
        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response[json_start:json_end]
                return json.loads(json_text)
            else:
                logger.warning("No valid JSON found in response")
                return {
                    "overall_risk": "Medium",
                    "business_impact": "Unable to fully assess business impact due to processing error",
                    "risk_factors": ["Incomplete risk assessment"],
                    "recommendations": ["Consult with a security expert for a complete assessment"]
                }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return {
                "error": "Could not parse response as JSON",
                "raw_response": response
            }
    
    def analyze_repository_security(self, tech_stack):
        """Main analysis function that combines all capabilities."""
        # Step 1: Analyze vulnerabilities
        analysis_result = self.analyze_technologies(tech_stack)
        vulnerabilities = analysis_result.get('vulnerabilities', [])
        
        # Step 2: Generate detailed test cases for each vulnerability
        for vuln in vulnerabilities:
            vuln['detailed_test_cases'] = self.generate_test_cases(vuln)
        
        # Step 3: Perform risk assessment
        risk_assessment = self.assess_risk(tech_stack, vulnerabilities)
        
        # Combine all results
        return {
            'tech_stack': tech_stack,
            'vulnerabilities': vulnerabilities,
            'risk_assessment': risk_assessment
        }

# Create a singleton instance
security_agent = SecurityAgent() 