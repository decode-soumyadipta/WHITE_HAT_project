# SHIELD: Synthetic Hacking Intelligence for Enhanced Liability Defense

SHIELD is a cybersecurity platform that transforms security operations by creating a continuous security improvement cycle with four key capabilities:

1. **Threat Intelligence Analysis**: Automatically monitors threat feeds, dark web chatter, and security bulletins to identify emerging threats relevant to the organization's technology stack.

2. **Automated Test Case Generation**: Creates comprehensive penetration testing scenarios based on the organization's infrastructure, without impacting production systems.

3. **Attack Simulation & Vulnerability Discovery**: Safely simulates attacks in a sandbox environment to identify exploitable vulnerabilities before real attackers can.

4. **Prioritized Remediation Planning**: Generates actionable remediation plans ranked by business impact, resource requirements, and implementation complexity.

## Setup Instructions

### Prerequisites

- Python 3.9+ 
- Node.js 16+
- PostgreSQL (optional, SQLite used by default)
- OpenAI API Key

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd shield/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Configure environment variables:
   - Edit the `.env` file and set your OpenAI API key and database configuration

6. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Run the backend server:
   ```
   flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd shield/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the frontend development server:
   ```
   npm start
   ```

## Features

### Threat Intelligence Analysis
- Integration with threat intelligence feeds
- AI-powered threat relevance assessment
- Automatic vulnerability identification based on tech stack

### Test Case Generation
- Infrastructure-aware security testing
- Automated test case generation for common vulnerabilities
- Customizable testing scenarios

### Attack Simulation
- Sandbox environment for safe attack simulation
- Vulnerability identification without production impact
- Detailed simulation results and impact analysis

### Risk Prioritization
- Business impact assessment
- Resource requirement estimations
- Implementation complexity analysis
- Prioritized remediation planning

## Usage

1. Register and create an organization
2. Define your technology stack
3. Run a threat intelligence analysis
4. Generate test cases for your environment
5. Simulate attacks to identify vulnerabilities
6. Review the executive dashboard for prioritized actions

## Technologies Used

- **Backend**: Flask, SQLAlchemy, LangChain, OpenAI
- **Frontend**: React, Chart.js, TailwindCSS
- **Database**: SQLite/PostgreSQL

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 