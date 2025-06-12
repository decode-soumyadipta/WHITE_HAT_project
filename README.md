
          
# 🛡️ SHIELD - Security Hub for Intelligent Entry-Level Defense

![GitHub](https://img.shields.io/badge/GitHub-Integration-181717?style=for-the-badge&logo=github)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.2.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Security](https://img.shields.io/badge/Security-Analysis-D14836?style=for-the-badge&logo=shield&logoColor=white)

## 📋 Overview

SHIELD is an advanced, integrated security assessment platform that leverages AI agents to automate vulnerability scanning, penetration testing, and threat hunting. This comprehensive tool helps identify security vulnerabilities in applications and provides detailed remediation recommendations, making enterprise-grade security accessible to developers and organizations of all sizes.


## 📸 Screenshots 

# 🔵Github Api Connect-
![image](https://github.com/user-attachments/assets/5e675bf0-ad88-4f53-8e6f-8f293ffb74a2)

# 🔵Ai Agent Scan Interface-
![image](https://github.com/user-attachments/assets/30ab3e16-d84a-4bc8-a520-0daf531698f1)

# 🔵LLM Input Prompt-
![image](https://github.com/user-attachments/assets/ce17b03e-83c4-42ea-9479-f3edd4817b74)

# 🟡LLM Output JSON-
![image](https://github.com/user-attachments/assets/7e5246ce-7c15-4af9-90a0-88bcc7b67341)






## 🌟 Key Features

### 🔍 Vulnerability Management
- **Comprehensive Tracking**: Monitor and manage security vulnerabilities across all your applications
- **Severity Classification**: Automatic categorization of vulnerabilities by criticality (Critical, High, Medium, Low)
- **CVSS Scoring**: Industry-standard Common Vulnerability Scoring System integration
- **Status Tracking**: Follow vulnerabilities from discovery through remediation

### 🤖 AI-Powered Analysis
- **Intelligent Scanning**: AI agents identify and prioritize security issues
- **Contextual Understanding**: Analysis considers your specific technology stack and application architecture
- **Automated Remediation Suggestions**: AI-generated fix recommendations
- **Natural Language Explanations**: Complex security concepts explained in understandable terms

### 🧪 Automated Test Cases
- **Dynamic Test Generation**: Create security test cases based on your specific technology stack
- **Execution Framework**: Run tests against your applications automatically
- **Result Analysis**: Detailed reporting on test outcomes
- **Continuous Integration**: Integrate security testing into your CI/CD pipeline

### 🔄 GitHub Integration
- **Repository Scanning**: Direct connection to GitHub repositories
- **Commit Analysis**: Identify vulnerabilities introduced in specific commits
- **PR Scanning**: Automated security checks on pull requests
- **OAuth Authentication**: Secure GitHub account connection

### 📊 Detailed Reporting
- **Interactive Dashboards**: Visual representation of security posture
- **Trend Analysis**: Track security improvements over time
- **Export Capabilities**: Generate reports in multiple formats
- **Business Impact Assessment**: Understand the potential business consequences of vulnerabilities

### 🏢 Organization Management
- **Multi-Organization Support**: Group and manage security assessments by organization
- **Role-Based Access Control**: Granular permissions for team members
- **Centralized View**: Consolidated security posture across all projects

## 🛠️ Technical Architecture

### Backend Technology Stack
- **Python 3.8+**: Core programming language
- **Flask 2.2.3**: Web framework for the application
- **SQLite**: Database for storing application data
- **Jinja2 3.1.2**: Templating engine for dynamic HTML generation
- **Werkzeug 2.2.3**: WSGI web application library
- **OpenAI 0.28.1**: Integration with AI models for analysis
- **LangChain 0.0.340**: Framework for developing applications with LLMs
- **PyGithub 1.59.0**: GitHub API integration
- **Docker 6.1.3**: Container management for isolated testing environments
- **Flask-SocketIO 5.3.6**: Real-time communication between server and clients

### Frontend Technology Stack
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome 6**: Icon library
- **JavaScript**: Client-side interactivity
- **Chart.js**: Data visualization
- **Socket.IO**: Real-time updates and notifications

### AI Components
- **Local LLM Integration**: Support for local LLM models like deepseek-coder
- **Automated Assessment Engine**: AI-powered security analysis
- **Test Case Generator**: AI-driven security test creation
- **Vulnerability Detection**: Pattern recognition for identifying security issues

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Git
- GitHub OAuth App (for repository integration)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/shield.git
   cd shield
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```
   
   **Activate the virtual environment**:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure GitHub Integration**:
   - Create a GitHub OAuth application:
     - Go to GitHub account settings
     - Navigate to "Developer settings" > "OAuth Apps" > "New OAuth App"
     - Application name: SHIELD Security Hub
     - Homepage URL: http://localhost:5000
     - Authorization callback URL: http://localhost:5000/github/callback
   - Set environment variables:
     ```bash
     set GITHUB_CLIENT_ID=your_client_id
     set GITHUB_CLIENT_SECRET=your_client_secret
     ```

## 🚀 Running the Application

### Development Mode

1. **Set Flask environment variables**:
   ```bash
   set FLASK_APP=app.py
   ```

2. **Run the application**:
   ```bash
   flask run
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### First-time Setup

1. **Login** using the default credentials:
   - Username: `admin`
   - Password: `password`

2. **Connect your GitHub account** through the profile page

3. **Create an organization** to group your security assessments

4. **Add repositories** for security scanning

## 💻 Usage Guide

### Running Security Assessments

1. **Navigate to AI Agent Automation**:
   - Select the repository to scan
   - Choose the LLM model for analysis
   - Select the assessment type (Repository Scanner, Vulnerability Scan, etc.)
   - Configure assessment options
   - Click "Run Assessment"

2. **View Results**:
   - Monitor real-time progress on the assessment page
   - Review detected vulnerabilities
   - Examine AI-generated test cases

### Managing Vulnerabilities

1. **Vulnerability Dashboard**:
   - Filter vulnerabilities by severity, status, and source
   - Sort and search for specific issues
   - View detailed information for each vulnerability

2. **Remediation**:
   - Review AI-suggested fixes
   - Mark vulnerabilities as "In Progress" or "Resolved"
   - Add notes and track remediation efforts

### Organization Management

1. **Create and Manage Organizations**:
   - Group related projects and repositories
   - Invite team members
   - Set permissions and access controls

2. **Dashboard Views**:
   - Organization-level security metrics
   - Project-specific vulnerability statistics
   - Trend analysis and security posture tracking

## 🔌 API Integration

SHIELD provides a RESTful API for integration with other tools and systems:

- **Authentication**: OAuth 2.0 token-based authentication
- **Endpoints**: Comprehensive API for accessing all SHIELD functionality
- **Webhooks**: Event-driven notifications for security events

## 📁 Project Structure

```
/shield
  /backend
    /app
      /api
        __init__.py
        routes.py
      /auth
        __init__.py
        routes.py
      /models
        __init__.py
        user.py
        organization.py
        vulnerability.py
        test_case.py
      /services
        __init__.py
        threat_intelligence.py
        test_case_generator.py
        attack_simulator.py
        risk_analyzer.py
      /utils
        __init__.py
        helpers.py
      __init__.py
      config.py
      extensions.py
    /migrations
    .env
    .flaskenv
    requirements.txt
  /frontend
    /public
    /src
      /components
      /pages
      /assets
      /utils
    package.json
  docker-compose.yml
  README.md
```

## 🧩 Core Components

### `/templates`
Contains HTML templates for the application UI, including:
- `base.html`: Main layout template
- `dashboard.html`: Security metrics dashboard
- `ai_agent_automation.html`: AI assessment configuration
- `vulnerabilities.html`: Vulnerability management interface
- `vulnerability_detail.html`: Detailed vulnerability information

### `/static`
Static assets for the frontend:
- `/css/main.css`: Custom styling
- `/js/main.js`: Client-side functionality

### `app.py`
Main application file containing:
- Flask routes and controllers
- Database connections and models
- Business logic for security assessments
- API endpoints

### `ai_agent_automation.py`
Implements the AI-powered security assessment engine:
- GitHub repository integration
- LLM model integration
- Vulnerability detection algorithms
- Test case generation

### `shield.db`
SQLite database storing:
- User accounts and organizations
- Repository information
- Vulnerability data
- Test cases and results

## 🤝 Contributing

Contributions are welcome! To contribute to SHIELD:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔒 Security Considerations

- SHIELD is designed for authorized security testing only
- Always obtain proper permission before scanning systems
- Follow responsible disclosure practices for any vulnerabilities discovered
- Use secure credentials and API keys when configuring the application

## 📚 Additional Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [CVSS Scoring System](https://www.first.org/cvss/)
- [Common Weakness Enumeration (CWE)](https://cwe.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

<p align="center">🛡️ <strong>SHIELD</strong> - Making advanced security accessible to everyone</p>

        
