import React, { useState, useEffect, useCallback } from 'react';
import { 
    Container, Row, Col, Card, Button, Form, Alert, 
    Spinner, ListGroup, Badge, Modal, Tab, Tabs 
} from 'react-bootstrap';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
    faRobot, faCheck, faExclamationTriangle, 
    faList, faLock, faShieldAlt, faTerminal, faSitemap
} from '@fortawesome/free-solid-svg-icons';

const AIAgentAutomation = () => {
    const [organizations, setOrganizations] = useState([]);
    const [selectedOrg, setSelectedOrg] = useState('');
    const [techStack, setTechStack] = useState([]);
    const [techInput, setTechInput] = useState('');
    const [assessmentType, setAssessmentType] = useState('vuln_scan');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');
    const [testCases, setTestCases] = useState([]);
    const [vulnerabilities, setVulnerabilities] = useState([]);
    const [showResultModal, setShowResultModal] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    
    const navigate = useNavigate();
    
    // Define fetch functions with useCallback to avoid dependency issues
    const fetchTestCases = useCallback(async () => {
        try {
            const response = await axios.get(`/api/ai-agent-test-cases/${selectedOrg}`);
            setTestCases(response.data);
        } catch (err) {
            console.error('Failed to fetch test cases:', err);
        }
    }, [selectedOrg]);
    
    // Fetch vulnerabilities from API
    const fetchVulnerabilities = useCallback(async () => {
        try {
            const response = await axios.get(`/api/ai-agent-vulnerabilities/${selectedOrg}`);
            setVulnerabilities(response.data);
        } catch (err) {
            console.error('Failed to fetch vulnerabilities:', err);
        }
    }, [selectedOrg]);
    
    // Fetch organizations from API
    const fetchOrganizations = async () => {
        try {
            const response = await axios.get('/api/organizations');
            setOrganizations(response.data);
            if (response.data.length > 0) {
                setSelectedOrg(response.data[0].id);
                // If the organization has a tech stack, use it
                if (response.data[0].tech_stack) {
                    try {
                        const techStackData = JSON.parse(response.data[0].tech_stack);
                        setTechStack(Array.isArray(techStackData) ? techStackData : []);
                    } catch (e) {
                        setTechStack([]);
                    }
                }
            }
        } catch (err) {
            setError('Failed to fetch organizations');
            console.error(err);
        }
    };
    
    // Fetch organizations on component mount
    useEffect(() => {
        fetchOrganizations();
    }, []);
    
    // Fetch test cases and vulnerabilities when organization is selected
    useEffect(() => {
        if (selectedOrg) {
            fetchTestCases();
            fetchVulnerabilities();
        }
    }, [selectedOrg, fetchTestCases, fetchVulnerabilities]);
    
    // Handler for organization change
    const handleOrgChange = (e) => {
        const orgId = e.target.value;
        setSelectedOrg(orgId);
        
        // Update tech stack when organization changes
        const org = organizations.find(o => o.id.toString() === orgId);
        if (org && org.tech_stack) {
            try {
                const techStackData = JSON.parse(org.tech_stack);
                setTechStack(Array.isArray(techStackData) ? techStackData : []);
            } catch (e) {
                setTechStack([]);
            }
        } else {
            setTechStack([]);
        }
    };
    
    // Handler for adding technology to stack
    const handleAddTech = () => {
        if (techInput.trim() !== '' && !techStack.includes(techInput.trim())) {
            setTechStack([...techStack, techInput.trim()]);
            setTechInput('');
        }
    };
    
    // Handler for removing technology from stack
    const handleRemoveTech = (tech) => {
        setTechStack(techStack.filter(t => t !== tech));
    };
    
    // Handler for running the assessment
    const handleRunAssessment = async () => {
        if (!selectedOrg) {
            setError('Please select an organization');
            return;
        }
        
        if (techStack.length === 0) {
            setError('Please add at least one technology to the stack');
            return;
        }
        
        setLoading(true);
        setError('');
        
        try {
            const response = await axios.post('/api/ai-agent-assessment', {
                organization_id: selectedOrg,
                tech_stack: techStack,
                assessment_type: assessmentType
            });
            
            setResults(response.data);
            setShowResultModal(true);
            
            // Refresh test cases and vulnerabilities
            fetchTestCases();
            fetchVulnerabilities();
        } catch (err) {
            setError('Failed to run assessment: ' + (err.response?.data?.error || err.message));
            console.error(err);
        } finally {
            setLoading(false);
        }
    };
    
    // Handler for viewing test case details
    const handleViewTestCase = (id) => {
        navigate(`/test-cases/${id}`);
    };
    
    // Handler for viewing vulnerability details
    const handleViewVulnerability = (id) => {
        navigate(`/vulnerabilities/${id}`);
    };
    
    // Get severity badge color
    const getSeverityBadge = (severity) => {
        switch (severity) {
            case 'critical':
                return 'danger';
            case 'high':
                return 'warning';
            case 'medium':
                return 'primary';
            case 'low':
                return 'secondary';
            default:
                return 'info';
        }
    };

    return (
        <Container fluid className="p-4">
            <Row className="mb-4">
                <Col>
                    <h2 className="mb-3">
                        <FontAwesomeIcon icon={faRobot} className="me-2" />
                        AI Agent Automation
                    </h2>
                    <p className="text-muted">
                        Automate security assessments with AI agents that simulate real-world attacks in a sandbox environment.
                    </p>
                </Col>
            </Row>
            
            <Row>
                <Col md={4}>
                    <Card className="mb-4">
                        <Card.Header className="bg-primary text-white">
                            <h5 className="mb-0">Configure Assessment</h5>
                        </Card.Header>
                        <Card.Body>
                            {error && <Alert variant="danger">{error}</Alert>}
                            
                            <Form>
                                <Form.Group className="mb-3">
                                    <Form.Label>Organization</Form.Label>
                                    <Form.Select 
                                        value={selectedOrg} 
                                        onChange={handleOrgChange}
                                    >
                                        {organizations.map(org => (
                                            <option key={org.id} value={org.id}>{org.name}</option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>
                                
                                <Form.Group className="mb-3">
                                    <Form.Label>Assessment Type</Form.Label>
                                    <Form.Select
                                        value={assessmentType}
                                        onChange={(e) => setAssessmentType(e.target.value)}
                                    >
                                        <option value="vuln_scan">Vulnerability Scan</option>
                                        <option value="pentest">Penetration Test</option>
                                        <option value="threat_hunt">Threat Hunting</option>
                                    </Form.Select>
                                </Form.Group>
                                
                                <Form.Group className="mb-3">
                                    <Form.Label>Technology Stack</Form.Label>
                                    <div className="d-flex mb-2">
                                        <Form.Control
                                            type="text"
                                            placeholder="Add technology..."
                                            value={techInput}
                                            onChange={(e) => setTechInput(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTech())}
                                        />
                                        <Button 
                                            variant="secondary" 
                                            className="ms-2"
                                            onClick={handleAddTech}
                                        >
                                            Add
                                        </Button>
                                    </div>
                                    
                                    <div className="border rounded p-2 min-height-100">
                                        {techStack.map((tech, index) => (
                                            <Badge 
                                                key={index} 
                                                bg="info" 
                                                className="me-2 mb-2 p-2"
                                            >
                                                {tech}
                                                <span 
                                                    className="ms-2" 
                                                    style={{ cursor: 'pointer' }}
                                                    onClick={() => handleRemoveTech(tech)}
                                                >
                                                    &times;
                                                </span>
                                            </Badge>
                                        ))}
                                        {techStack.length === 0 && (
                                            <div className="text-muted p-2">No technologies added</div>
                                        )}
                                    </div>
                                </Form.Group>
                                
                                <Button 
                                    variant="primary" 
                                    className="w-100"
                                    onClick={handleRunAssessment}
                                    disabled={loading || !selectedOrg || techStack.length === 0}
                                >
                                    {loading ? (
                                        <>
                                            <Spinner 
                                                as="span"
                                                animation="border"
                                                size="sm"
                                                role="status"
                                                aria-hidden="true"
                                                className="me-2"
                                            />
                                            Running Assessment...
                                        </>
                                    ) : (
                                        <>
                                            <FontAwesomeIcon icon={faTerminal} className="me-2" />
                                            Run AI Assessment
                                        </>
                                    )}
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
                
                <Col md={8}>
                    <Tabs
                        activeKey={activeTab}
                        onSelect={(k) => setActiveTab(k)}
                        className="mb-3"
                    >
                        <Tab eventKey="overview" title="Overview">
                            <Card className="mb-4">
                                <Card.Header className="bg-info text-white">
                                    <h5 className="mb-0">AI Agent Automation Overview</h5>
                                </Card.Header>
                                <Card.Body>
                                    <div className="mb-4">
                                        <h6>
                                            <FontAwesomeIcon icon={faShieldAlt} className="me-2" />
                                            How It Works
                                        </h6>
                                        <p>
                                            The AI Agent Automation system uses advanced language models to simulate real-world
                                            attacks against your systems in a safe, sandboxed environment. Here's the process:
                                        </p>
                                        <ol>
                                            <li>The system analyzes your technology stack to identify potential vulnerabilities</li>
                                            <li>AI agents generate targeted test cases based on your specific technologies</li>
                                            <li>Each test is executed in a sandboxed environment to simulate attacks</li>
                                            <li>Results are analyzed to identify genuine vulnerabilities with remediation steps</li>
                                        </ol>
                                    </div>
                                    
                                    <div>
                                        <h6>
                                            <FontAwesomeIcon icon={faSitemap} className="me-2" />
                                            Assessment Types
                                        </h6>
                                        <ul>
                                            <li><strong>Vulnerability Scan:</strong> Identifies common security issues in your tech stack</li>
                                            <li><strong>Penetration Test:</strong> Simulates targeted attacks against specific systems</li>
                                            <li><strong>Threat Hunting:</strong> Searches for evidence of existing compromises</li>
                                        </ul>
                                    </div>
                                </Card.Body>
                            </Card>
                            
                            <Row>
                                <Col md={6}>
                                    <Card className="mb-4">
                                        <Card.Header className="bg-primary text-white">
                                            <h5 className="mb-0">
                                                <FontAwesomeIcon icon={faList} className="me-2" />
                                                Recent Test Cases
                                            </h5>
                                        </Card.Header>
                                        <ListGroup variant="flush">
                                            {testCases.slice(0, 5).map((testCase) => (
                                                <ListGroup.Item 
                                                    key={testCase.id}
                                                    action
                                                    onClick={() => handleViewTestCase(testCase.id)}
                                                >
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <strong>{testCase.name}</strong>
                                                            <div className="small text-muted">{testCase.type}</div>
                                                        </div>
                                                        <Badge bg={
                                                            testCase.status === 'completed' ? 'success' : 
                                                            testCase.status === 'failed' ? 'danger' : 
                                                            testCase.status === 'running' ? 'warning' : 'secondary'
                                                        }>
                                                            {testCase.status}
                                                        </Badge>
                                                    </div>
                                                </ListGroup.Item>
                                            ))}
                                            {testCases.length === 0 && (
                                                <ListGroup.Item className="text-center text-muted py-4">
                                                    No test cases available
                                                </ListGroup.Item>
                                            )}
                                        </ListGroup>
                                    </Card>
                                </Col>
                                
                                <Col md={6}>
                                    <Card className="mb-4">
                                        <Card.Header className="bg-danger text-white">
                                            <h5 className="mb-0">
                                                <FontAwesomeIcon icon={faLock} className="me-2" />
                                                Recent Vulnerabilities
                                            </h5>
                                        </Card.Header>
                                        <ListGroup variant="flush">
                                            {vulnerabilities.slice(0, 5).map((vuln) => (
                                                <ListGroup.Item 
                                                    key={vuln.id}
                                                    action
                                                    onClick={() => handleViewVulnerability(vuln.id)}
                                                >
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <strong>{vuln.title}</strong>
                                                            <div className="small text-muted">
                                                                CVSS: {vuln.cvss_score || 'N/A'}
                                                            </div>
                                                        </div>
                                                        <Badge bg={getSeverityBadge(vuln.severity)}>
                                                            {vuln.severity}
                                                        </Badge>
                                                    </div>
                                                </ListGroup.Item>
                                            ))}
                                            {vulnerabilities.length === 0 && (
                                                <ListGroup.Item className="text-center text-muted py-4">
                                                    No vulnerabilities discovered
                                                </ListGroup.Item>
                                            )}
                                        </ListGroup>
                                    </Card>
                                </Col>
                            </Row>
                        </Tab>
                        
                        <Tab eventKey="testCases" title="Test Cases">
                            <Card>
                                <Card.Header className="bg-primary text-white">
                                    <h5 className="mb-0">AI-Generated Test Cases</h5>
                                </Card.Header>
                                <Card.Body className="p-0">
                                    <ListGroup variant="flush">
                                        {testCases.map((testCase) => (
                                            <ListGroup.Item 
                                                key={testCase.id}
                                                action
                                                onClick={() => handleViewTestCase(testCase.id)}
                                            >
                                                <div className="d-flex justify-content-between align-items-center mb-2">
                                                    <h6 className="mb-0">{testCase.name}</h6>
                                                    <Badge bg={
                                                        testCase.status === 'completed' ? 'success' : 
                                                        testCase.status === 'failed' ? 'danger' : 
                                                        testCase.status === 'running' ? 'warning' : 'secondary'
                                                    }>
                                                        {testCase.status}
                                                    </Badge>
                                                </div>
                                                <div className="mb-2">{testCase.description}</div>
                                                <div className="d-flex small text-muted">
                                                    <div className="me-3">Type: {testCase.type}</div>
                                                    <div>Target: {testCase.target}</div>
                                                </div>
                                            </ListGroup.Item>
                                        ))}
                                        {testCases.length === 0 && (
                                            <ListGroup.Item className="text-center text-muted py-4">
                                                No test cases available
                                            </ListGroup.Item>
                                        )}
                                    </ListGroup>
                                </Card.Body>
                            </Card>
                        </Tab>
                        
                        <Tab eventKey="vulnerabilities" title="Vulnerabilities">
                            <Card>
                                <Card.Header className="bg-danger text-white">
                                    <h5 className="mb-0">Discovered Vulnerabilities</h5>
                                </Card.Header>
                                <Card.Body className="p-0">
                                    <ListGroup variant="flush">
                                        {vulnerabilities.map((vuln) => (
                                            <ListGroup.Item 
                                                key={vuln.id}
                                                action
                                                onClick={() => handleViewVulnerability(vuln.id)}
                                            >
                                                <div className="d-flex justify-content-between align-items-center mb-2">
                                                    <h6 className="mb-0">{vuln.title}</h6>
                                                    <Badge bg={getSeverityBadge(vuln.severity)}>
                                                        {vuln.severity}
                                                    </Badge>
                                                </div>
                                                <div className="mb-2">{vuln.description}</div>
                                                <div className="d-flex small text-muted">
                                                    <div className="me-3">CVSS: {vuln.cvss_score || 'N/A'}</div>
                                                    <div>Status: {vuln.status}</div>
                                                </div>
                                            </ListGroup.Item>
                                        ))}
                                        {vulnerabilities.length === 0 && (
                                            <ListGroup.Item className="text-center text-muted py-4">
                                                No vulnerabilities discovered
                                            </ListGroup.Item>
                                        )}
                                    </ListGroup>
                                </Card.Body>
                            </Card>
                        </Tab>
                    </Tabs>
                </Col>
            </Row>
            
            {/* Results Modal */}
            <Modal 
                show={showResultModal} 
                onHide={() => setShowResultModal(false)}
                size="lg"
            >
                <Modal.Header closeButton>
                    <Modal.Title>Assessment Results</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {results && (
                        <div>
                            <Alert 
                                variant={results.vulnerabilities_found > 0 ? 'warning' : 'success'}
                                className="mb-4"
                            >
                                <div className="d-flex align-items-center">
                                    <FontAwesomeIcon 
                                        icon={results.vulnerabilities_found > 0 ? faExclamationTriangle : faCheck} 
                                        className="me-2 fa-lg" 
                                    />
                                    <div>
                                        <strong>
                                            {results.vulnerabilities_found > 0 
                                                ? `${results.vulnerabilities_found} vulnerabilities found!` 
                                                : 'No vulnerabilities found!'}
                                        </strong>
                                        <div>
                                            {results.vulnerabilities_found > 0 
                                                ? 'Review the detailed findings and take action to secure your systems.' 
                                                : 'Your systems appear to be secure against the tested attack vectors.'}
                                        </div>
                                    </div>
                                </div>
                            </Alert>
                            
                            <div className="mb-4">
                                <h6>Assessment Summary</h6>
                                <table className="table table-bordered">
                                    <tbody>
                                        <tr>
                                            <th>Assessment ID</th>
                                            <td>{results.assessment_id}</td>
                                        </tr>
                                        <tr>
                                            <th>Organization</th>
                                            <td>{organizations.find(o => o.id.toString() === selectedOrg.toString())?.name}</td>
                                        </tr>
                                        <tr>
                                            <th>Type</th>
                                            <td>{results.assessment_type}</td>
                                        </tr>
                                        <tr>
                                            <th>Test Cases</th>
                                            <td>{results.test_cases_count}</td>
                                        </tr>
                                        <tr>
                                            <th>Vulnerabilities</th>
                                            <td>{results.vulnerabilities_found}</td>
                                        </tr>
                                        <tr>
                                            <th>Timestamp</th>
                                            <td>{new Date(results.timestamp).toLocaleString()}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            
                            {results.vulnerabilities_found > 0 && (
                                <div>
                                    <h6>Vulnerability Summary</h6>
                                    <ListGroup variant="flush">
                                        {results.vulnerabilities.map((vuln, index) => (
                                            <ListGroup.Item 
                                                key={index}
                                                className="border rounded mb-2"
                                            >
                                                <div className="d-flex justify-content-between align-items-center mb-2">
                                                    <h6 className="mb-0">{vuln.title}</h6>
                                                    <Badge bg={getSeverityBadge(vuln.severity)}>
                                                        {vuln.severity}
                                                    </Badge>
                                                </div>
                                                <div>{vuln.description}</div>
                                                {vuln.remediation_plan && (
                                                    <div className="mt-2">
                                                        <strong>Remediation:</strong> {vuln.remediation_plan}
                                                    </div>
                                                )}
                                            </ListGroup.Item>
                                        ))}
                                    </ListGroup>
                                </div>
                            )}
                        </div>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowResultModal(false)}>
                        Close
                    </Button>
                    <Button 
                        variant="primary" 
                        onClick={() => {
                            setShowResultModal(false);
                            setActiveTab('vulnerabilities');
                        }}
                    >
                        View All Vulnerabilities
                    </Button>
                </Modal.Footer>
            </Modal>
        </Container>
    );
};

export default AIAgentAutomation; 