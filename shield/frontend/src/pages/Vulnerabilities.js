import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Vulnerabilities = () => {
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [organizations, setOrganizations] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState('');
  const [showAIDetectionForm, setShowAIDetectionForm] = useState(false);
  const [aiDetectionFormData, setAIDetectionFormData] = useState({
    repo_url: '',
    branch: 'main',
    organization_id: ''
  });
  const [aiScanning, setAIScanning] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // Fetch vulnerabilities
        const vulnResponse = await axios.get(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/vulnerabilities`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        setVulnerabilities(vulnResponse.data);
        
        // Fetch organizations for filter
        const orgsResponse = await axios.get(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/organizations`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        setOrganizations(orgsResponse.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch vulnerabilities');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleOrgChange = (e) => {
    setSelectedOrg(e.target.value);
  };

  const handleAIDetectionInputChange = (e) => {
    setAIDetectionFormData({
      ...aiDetectionFormData,
      [e.target.name]: e.target.value
    });
  };

  const handleAIDetectionSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setAIScanning(true);
    
    try {
      const token = localStorage.getItem('token');
      
      // Step 1: Call GitHub API to analyze repository
      const analyzeResponse = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/github/analyze`,
        {
          repo_url: aiDetectionFormData.repo_url,
          branch: aiDetectionFormData.branch
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      const analysisResult = analyzeResponse.data.data;
      
      if (!analysisResult || !analysisResult.vulnerabilities) {
        throw new Error('No vulnerabilities detected from repository analysis');
      }
      
      // Step 2: Create vulnerabilities from analysis results
      for (const vuln of analysisResult.vulnerabilities) {
        await axios.post(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/vulnerabilities`,
          {
            organization_id: aiDetectionFormData.organization_id,
            name: vuln.name,
            description: vuln.description,
            severity: vuln.severity || 'Medium',
            status: 'Open',
            affected_components: vuln.affected_components || 'Not specified',
            remediation: vuln.recommendation || 'Not provided',
            details: JSON.stringify({
              source: 'AI Detected',
              repo_url: aiDetectionFormData.repo_url,
              cvss_score: vuln.cvss_score || 5.0,
              attack_vector: vuln.attack_vector || 'Not specified'
            })
          },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
      }
      
      // Reset form and refresh vulnerabilities
      setAIDetectionFormData({
        repo_url: '',
        branch: 'main',
        organization_id: ''
      });
      setShowAIDetectionForm(false);
      
      // Fetch updated vulnerabilities
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/vulnerabilities`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      setVulnerabilities(response.data);
    } catch (err) {
      setError('Failed to detect vulnerabilities: ' + (err.message || 'Unknown error'));
    } finally {
      setAIScanning(false);
    }
  };

  const filteredVulnerabilities = selectedOrg 
    ? vulnerabilities.filter(vuln => vuln.organization_id === parseInt(selectedOrg))
    : vulnerabilities;

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-600 text-white';
      case 'high':
        return 'bg-red-500 text-white';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500 text-white';
      case 'info':
        return 'bg-gray-500 text-white';
      default:
        return 'bg-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-red-100 text-red-800';
      case 'in progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Vulnerabilities</h1>
        <button
          onClick={() => setShowAIDetectionForm(!showAIDetectionForm)}
          className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
        >
          {showAIDetectionForm ? 'Cancel' : 'AI Vulnerability Detection'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {showAIDetectionForm && (
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">AI-Powered Vulnerability Detection</h2>
          <p className="text-gray-600 mb-4">
            Connect to a GitHub repository to automatically detect security vulnerabilities based on code analysis.
          </p>
          <form onSubmit={handleAIDetectionSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="repo_url">
                  GitHub Repository URL
            </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="repo_url"
                  type="text"
                  name="repo_url"
                  placeholder="https://github.com/username/repository"
                  value={aiDetectionFormData.repo_url}
                  onChange={handleAIDetectionInputChange}
                  required
                />
          </div>
          <div>
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="branch">
                  Branch
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="branch"
                  type="text"
                  name="branch"
                  placeholder="main"
                  value={aiDetectionFormData.branch}
                  onChange={handleAIDetectionInputChange}
                />
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="organization_id">
                Organization
            </label>
            <select
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="organization_id"
                name="organization_id"
                value={aiDetectionFormData.organization_id}
                onChange={handleAIDetectionInputChange}
                required
              >
                <option value="">Select Organization</option>
                {organizations.map(org => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
            </select>
          </div>
            <div className="flex justify-end">
              <button
                type="submit"
                className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded flex items-center"
                disabled={aiScanning}
              >
                {aiScanning ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Scanning...
                  </>
                ) : (
                  'Detect Vulnerabilities'
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="w-64">
            <label htmlFor="org-filter" className="block text-sm font-medium text-gray-700">
              Filter by Organization
            </label>
            <select
              id="org-filter"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={selectedOrg}
              onChange={handleOrgChange}
            >
              <option value="">All Organizations</option>
              {organizations.map(org => (
                <option key={org.id} value={org.id}>{org.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {filteredVulnerabilities.length === 0 ? (
        <div className="bg-white shadow-md rounded-lg p-6 text-center text-gray-500">
          No vulnerabilities found for the selected criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredVulnerabilities.map(vuln => (
            <div key={vuln.id} className="bg-white shadow-md rounded-lg overflow-hidden">
              <div className={`p-4 ${getSeverityColor(vuln.severity)}`}>
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium truncate">{vuln.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(vuln.status)}`}>
                    {vuln.status}
                  </span>
                </div>
              </div>
              <div className="p-4">
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{vuln.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    {organizations.find(org => org.id === vuln.organization_id)?.name || 'Unknown Organization'}
                  </span>
                  <Link
                    to={`/vulnerability/${vuln.id}`}
                    className="text-blue-500 hover:text-blue-700 text-sm font-medium"
                  >
                    View Details →
          </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Vulnerabilities; 