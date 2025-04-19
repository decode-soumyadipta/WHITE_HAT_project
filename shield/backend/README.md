# Shield Backend

The backend server for the Shield application, an AI-powered security analysis tool.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- An OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd shield/backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   # Create .env file from the example
   cp .env.example .env
   
   # Edit the .env file to set your OpenAI API key and other configurations
   ```

5. Initialize the database:
   ```
   # This will be done automatically when you run the app
   # but you can also run it manually with:
   flask db init
   flask db migrate
   flask db upgrade
   ```

### Running the Application

Start the development server:
```
python run.py
```

The server will run on http://localhost:5000 by default.

### Testing LangChain Integration

You can test if LangChain is properly configured by running:
```
python test_langchain.py
```

## API Endpoints

### GitHub Repository Analysis
- `POST /api/github/analyze` - Analyze a GitHub repository for security vulnerabilities
  - Request body: `{"repo_url": "https://github.com/username/repo", "branch": "main"}`

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Vulnerabilities
- `GET /api/vulnerabilities` - Get list of vulnerabilities
- `GET /api/vulnerabilities/:id` - Get vulnerability details

### Test Cases
- `GET /api/test-cases` - Get list of test cases
- `POST /api/test-cases/run` - Run a test case

## Architecture

The backend uses a Flask-based architecture with:
- SQLAlchemy for database ORM
- LangChain for AI integration
- OpenAI API for language model capabilities
- Flask-JWT for authentication

## Troubleshooting

If you encounter issues with LangChain integration:
1. Verify your OpenAI API key is set correctly in the .env file
2. Make sure you have installed the latest versions of langchain packages
3. Run the test_langchain.py script to verify connectivity 