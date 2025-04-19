"""
Test script to verify LangChain integration is working properly.
"""
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def test_langchain_connection():
    """Test basic LangChain and OpenAI integration."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return False
    
    try:
        # Initialize the model
        model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=api_key
        )
        
        # Create a simple message
        message = HumanMessage(content="Hello, can you tell me what LangChain is in one sentence?")
        
        # Call the model
        response = model.invoke([message])
        
        # Print the response
        print("\nLangChain Test Successful!")
        print("-" * 40)
        print(f"Response: {response.content}")
        print("-" * 40)
        
        return True
    except Exception as e:
        print(f"Error testing LangChain: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing LangChain integration...")
    success = test_langchain_connection()
    
    if success:
        print("\nLangChain is properly configured.")
    else:
        print("\nLangChain integration test failed.") 