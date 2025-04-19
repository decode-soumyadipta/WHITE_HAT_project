import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Container, CircularProgress, Alert, Divider, Chip, Card, CardContent, Grid, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import GitHubIcon from '@mui/icons-material/GitHub';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import SecurityIcon from '@mui/icons-material/Security';
import BugReportIcon from '@mui/icons-material/BugReport';
import AssessmentIcon from '@mui/icons-material/Assessment';

const GitHubAnalyzer = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [step, setStep] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult(null);
    setStep(1);

    try {
      const response = await fetch('/api/github/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          branch: branch,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to analyze repository');
      }

      setResult(data.data);
      setStep(5); // Analysis complete
    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const renderTechStack = (techStack) => {
    if (!techStack) return null;

    return (
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Detected Technology Stack
        </Typography>
        <Grid container spacing={2}>
          {techStack.languages && techStack.languages.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <CodeIcon sx={{ mr: 1 }} />
                    Languages
                  </Typography>
                  <Box mt={1}>
                    {techStack.languages.map((lang) => (
                      <Chip key={lang} label={lang} sx={{ m: 0.5 }} />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {techStack.frameworks && techStack.frameworks.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <CodeIcon sx={{ mr: 1 }} />
                    Frameworks
                  </Typography>
                  <Box mt={1}>
                    {techStack.frameworks.map((framework) => (
                      <Chip key={framework} label={framework} sx={{ m: 0.5 }} />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {techStack.databases && techStack.databases.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <StorageIcon sx={{ mr: 1 }} />
                    Databases
                  </Typography>
                  <Box mt={1}>
                    {techStack.databases.map((db) => (
                      <Chip key={db} label={db} sx={{ m: 0.5 }} />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {techStack.cloud_services && techStack.cloud_services.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center' }}>
                    <CloudIcon sx={{ mr: 1 }} />
                    Cloud Services
                  </Typography>
                  <Box mt={1}>
                    {techStack.cloud_services.map((service) => (
                      <Chip key={service} label={service} sx={{ m: 0.5 }} />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Box>
    );
  };

  const renderVulnerabilities = (vulnerabilities) => {
    if (!vulnerabilities || vulnerabilities.length === 0) return null;

    return (
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Detected Vulnerabilities
        </Typography>
        {vulnerabilities.map((vuln, index) => (
          <Accordion key={index}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography sx={{ fontWeight: 'bold', color: vuln.severity === 'high' ? 'error.main' : (vuln.severity === 'medium' ? 'warning.main' : 'info.main') }}>
                {vuln.name} - {vuln.severity.toUpperCase()}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                {vuln.description}
              </Typography>
              <Typography variant="subtitle2">Affected Components:</Typography>
              <Typography variant="body2" paragraph>
                {vuln.affected_components}
              </Typography>
              <Typography variant="subtitle2">Recommendation:</Typography>
              <Typography variant="body2">
                {vuln.recommendation}
              </Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  const renderTestCases = (testCases) => {
    if (!testCases || testCases.length === 0) return null;

    return (
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          <BugReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Security Test Cases
        </Typography>
        {testCases.map((testCase, index) => (
          <Accordion key={index}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>
                {testCase.name}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                {testCase.description}
              </Typography>
              <Typography variant="subtitle2">Steps:</Typography>
              <ol>
                {testCase.steps.map((step, stepIndex) => (
                  <li key={stepIndex}>{step}</li>
                ))}
              </ol>
              <Typography variant="subtitle2" sx={{ mt: 1 }}>Expected Result:</Typography>
              <Typography variant="body2">
                {testCase.expected_result}
              </Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  const renderAnalysisResults = () => {
    if (!result) return null;

    return (
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Analysis Results
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {result.output && (
          <Box mb={3}>
            <Typography variant="body1" whiteSpace="pre-wrap">
              {result.output}
            </Typography>
          </Box>
        )}

        {renderTechStack(result.tech_stack)}
        {renderVulnerabilities(result.vulnerabilities)}
        {renderTestCases(result.test_cases)}

        {result.risk_analysis && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Risk Analysis
            </Typography>
            <Typography variant="body1" paragraph>
              {result.risk_analysis.summary}
            </Typography>
            {result.risk_analysis.financial_impact && (
              <Typography variant="body2">
                <strong>Estimated Financial Impact:</strong> {result.risk_analysis.financial_impact}
              </Typography>
            )}
          </Box>
        )}

        {result.recommendations && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            <ul>
              {result.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </Box>
        )}
      </Box>
    );
  };

  const renderStepIndicator = () => {
    const steps = [
      { label: 'Start', description: 'Enter repository URL' },
      { label: 'Cloning', description: 'Cloning the repository' },
      { label: 'Scanning', description: 'Scanning for technologies' },
      { label: 'Analyzing', description: 'Analyzing security issues' },
      { label: 'Testing', description: 'Running security tests' },
      { label: 'Complete', description: 'Analysis complete' }
    ];

    return (
      <Box sx={{ width: '100%', mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          {steps.map((s, i) => (
            <Box 
              key={i} 
              sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center',
                position: 'relative',
                width: `${100 / steps.length}%`
              }}
            >
              <Box 
                sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  bgcolor: i <= step ? 'primary.main' : 'grey.300',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  color: i <= step ? 'white' : 'text.secondary',
                  zIndex: 1
                }}
              >
                {i + 1}
              </Box>
              <Typography 
                variant="caption" 
                sx={{ 
                  mt: 1, 
                  textAlign: 'center',
                  color: i <= step ? 'text.primary' : 'text.secondary'
                }}
              >
                {s.label}
              </Typography>
              {i < steps.length - 1 && (
                <Box 
                  sx={{ 
                    position: 'absolute', 
                    width: '100%', 
                    height: 2, 
                    bgcolor: i < step ? 'primary.main' : 'grey.300',
                    top: 20,
                    left: '50%',
                    zIndex: 0
                  }} 
                />
              )}
            </Box>
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <GitHubIcon sx={{ fontSize: 32, mr: 2 }} />
          <Typography variant="h4">GitHub Repository Analyzer</Typography>
        </Box>
        <Typography variant="body1" paragraph>
          Connect to a GitHub repository to analyze security vulnerabilities and generate targeted test cases.
        </Typography>

        {renderStepIndicator()}

        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, mb: 3 }}>
            <TextField
              label="GitHub Repository URL"
              variant="outlined"
              fullWidth
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              required
              placeholder="https://github.com/username/repository"
              disabled={isLoading}
              sx={{ flexGrow: 1 }}
            />
            <TextField
              label="Branch"
              variant="outlined"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              disabled={isLoading}
              sx={{ width: { xs: '100%', md: '200px' } }}
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={isLoading}
              sx={{ height: { md: 56 }, width: { xs: '100%', md: 'auto' } }}
            >
              {isLoading ? <CircularProgress size={24} /> : "Analyze Repository"}
            </Button>
          </Box>
        </form>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {isLoading && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
            <CircularProgress />
            <Typography variant="h6" sx={{ mt: 2 }}>
              {step === 1 && "Cloning repository..."}
              {step === 2 && "Scanning for technologies..."}
              {step === 3 && "Analyzing security vulnerabilities..."}
              {step === 4 && "Running security tests..."}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              This process may take a few minutes depending on the repository size.
            </Typography>
          </Box>
        )}

        {renderAnalysisResults()}
      </Paper>
    </Container>
  );
};

export default GitHubAnalyzer; 