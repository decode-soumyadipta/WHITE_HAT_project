"""
Test script to verify OpenAI API integration is working properly.
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test basic OpenAI API integration."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return False
    
    try:
        # Configure OpenAI
        openai.api_key = api_key
        
        # Create a simple prompt
        prompt = "Hello, can you tell me what OpenAI is in one sentence?"
        
        # Call the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0
        )
        
        # Print the response
        print("\nOpenAI API Test Successful!")
        print("-" * 40)
        print(f"Response: {response.choices[0].text.strip()}")
        print("-" * 40)
        
        return True
    except Exception as e:
        print(f"Error testing OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API integration...")
    success = test_openai_connection()
    
    if success:
        print("\nOpenAI API is properly configured.")
    else:
        print("\nOpenAI API integration test failed.") 