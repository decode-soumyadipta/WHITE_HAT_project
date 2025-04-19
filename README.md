# SHIELD - Security Hub for Intelligent Entry-Level Defense

SHIELD is an integrated security assessment platform that uses AI agents to automate vulnerability scanning, penetration testing, and threat hunting. This tool helps identify security vulnerabilities in your applications and provides remediation recommendations.

## Features

- **Vulnerability Management**: Track and manage security vulnerabilities across your applications
- **Automated Test Cases**: Generate and execute security test cases based on your technology stack
- **AI-Powered Analysis**: Use AI agents to identify and prioritize security issues
- **Organization Management**: Group and manage security assessments by organization
- **Detailed Reporting**: Get comprehensive reports with actionable insights
- **GitHub Integration**: Connect to GitHub repositories for security scanning and analysis

## Requirements

- Python 3.8 or higher
- Flask
- SQLite
- GitHub OAuth App (for repository integration)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/shield.git
   cd shield
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```
   
   Activate the virtual environment:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install flask
   ```

## GitHub Integration

To enable GitHub integration, you need to create a GitHub OAuth application:

1. Go to your GitHub account settings
2. Navigate to "Developer settings" > "OAuth Apps" > "New OAuth App"
3. Fill in the following details:
   - Application name: SHIELD Security Hub
   - Homepage URL: http://localhost:5000
   - Authorization callback URL: http://localhost:5000/github/callback
4. Register the application and note your Client ID and Client Secret
5. Set these as environment variables before running the application:
   - Windows Command Prompt:
     ```
     set GITHUB_CLIENT_ID=your_client_id
     set GITHUB_CLIENT_SECRET=your_client_secret
     ```
   - Windows PowerShell:
     ```
     $env:GITHUB_CLIENT_ID = "your_client_id"
     $env:GITHUB_CLIENT_SECRET = "your_client_secret"
     ```
   - macOS/Linux:
     ```
     export GITHUB_CLIENT_ID=your_client_id
     export GITHUB_CLIENT_SECRET=your_client_secret
     ```

## Running the Application

### Windows (PowerShell)

Run the PowerShell script:
```
.\run_app.ps1
```

### Manual Method

1. Set the Flask application environment variable:
   - Windows Command Prompt:
     ```
     set FLASK_APP=app.py
     ```
   - Windows PowerShell:
     ```
     $env:FLASK_APP = "app.py"
     ```
   - macOS/Linux:
     ```
     export FLASK_APP=app.py
     ```

2. Run the Flask application:
   ```
   flask run
   ```

3. Access the application in your browser at:
   ```
   http://localhost:5000
   ```

## Getting Started

1. Access the application using your web browser
2. Login using the default credentials:
   - Username: `admin`
   - Password: `password`
3. Create or select an organization to assess
4. Navigate to the AI Agent Automation page to run security assessments

## Application Structure

- `/templates`: HTML templates for the application UI
- `/static`: Static assets (CSS, JavaScript, images)
- `app.py`: Main application code with routes and business logic
- `shield.db`: SQLite database storing application data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
