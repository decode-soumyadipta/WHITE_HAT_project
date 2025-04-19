import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../utils/AuthContext';
import { getOrganization, analyzeThreat } from '../utils/api';

const ThreatIntelligence = () => {
  const { user } = useContext(AuthContext);
  const [organization, setOrganization] = useState(null);
  const [techStack, setTechStack] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user && user.organization_id) {
      fetchOrganizationData(user.organization_id);
    }
  }, [user]);

  const fetchOrganizationData = async (orgId) => {
    setLoading(true);
    try {
      const response = await getOrganization(orgId);
      setOrganization(response.data);
      
      // Parse tech stack from JSON if available
      if (response.data.tech_stack) {
        try {
          setTechStack(JSON.parse(response.data.tech_stack));
        } catch (err) {
          console.error('Error parsing tech stack:', err);
          setTechStack([]);
        }
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching organization:', err);
      setError('Failed to load organization data. Please try again later.');
      setLoading(false);
    }
  };

  const handleTechStackChange = (e, index) => {
    const newTechStack = [...techStack];
    newTechStack[index] = e.target.value;
    setTechStack(newTechStack);
  };

  const addTechItem = () => {
    setTechStack([...techStack, '']);
  };

  const removeTechItem = (index) => {
    const newTechStack = [...techStack];
    newTechStack.splice(index, 1);
    setTechStack(newTechStack);
  };

  const runThreatAnalysis = async () => {
    if (!user || !user.organization_id) {
      setError('Organization ID is required to run threat analysis');
      return;
    }

    if (techStack.length === 0) {
      setError('Please add at least one technology to your stack');
      return;
    }

    setAnalyzing(true);
    setError(null);
    
    try {
      const response = await analyzeThreat({
        organization_id: user.organization_id,
        tech_stack: techStack.filter(tech => tech.trim() !== '')
      });
      
      setResults(response.data);
      setAnalyzing(false);
    } catch (err) {
      console.error('Error analyzing threats:', err);
      setError('Failed to analyze threats. Please try again later.');
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="text-xl font-semibold">Loading...</div>
      </div>
    );
  }

  if (!user || !user.organization_id) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
        <p>Please select or create an organization to run threat intelligence analysis.</p>
        <Link to="/organizations" className="text-blue-600 hover:underline mt-2 inline-block">
          Go to Organizations
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold mb-6">Threat Intelligence Analysis</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">
          {organization ? `Configure Analysis for ${organization.name}` : 'Configure Analysis'}
        </h2>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Technology Stack
          </label>
          <p className="text-gray-600 text-sm mb-2">
            Add technologies, frameworks, and services used in your environment
          </p>
          
          {techStack.map((tech, index) => (
            <div key={index} className="flex mb-2">
              <input
                type="text"
                value={tech}
                onChange={(e) => handleTechStackChange(e, index)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="e.g., React, Node.js, PostgreSQL, AWS Lambda"
              />
              <button
                onClick={() => removeTechItem(index)}
                className="ml-2 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                ✕
              </button>
            </div>
          ))}
          
          <button
            onClick={addTechItem}
            className="mt-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            + Add Technology
          </button>
        </div>
        
        <button
          onClick={runThreatAnalysis}
          disabled={analyzing}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {analyzing ? 'Analyzing Threats...' : 'Run Threat Analysis'}
        </button>
      </div>

      {results && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          
          <div className="mb-4">
            <p className="text-gray-700">
              <span className="font-semibold">Organization:</span> {organization?.name}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Technologies Analyzed:</span> {results.tech_stack.join(', ')}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Threats Identified:</span> {results.count}
            </p>
          </div>
          
          {results.threats && results.threats.length > 0 ? (
            <div>
              <h3 className="text-lg font-semibold mb-2">Identified Threats</h3>
              
              {results.threats.map((threat, index) => (
                <div key={index} className="mb-4 p-4 border rounded-lg">
                  <h4 className="text-md font-semibold">{threat.title}</h4>
                  <p className="text-sm text-gray-700 mb-2">{threat.description}</p>
                  
                  <div className="grid grid-cols-2 gap-4 mb-2">
                    <div>
                      <span className="text-xs font-semibold text-gray-500">CVSS Score</span>
                      <p className="text-md font-bold">{threat.cvss_score}</p>
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-gray-500">Severity</span>
                      <p className={`text-md font-bold severity-${threat.severity}`}>
                        {threat.severity.charAt(0).toUpperCase() + threat.severity.slice(1)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <span className="text-xs font-semibold text-gray-500">Affected Systems</span>
                    <p className="text-sm">{threat.affected_systems.join(', ')}</p>
                  </div>
                  
                  <div>
                    <span className="text-xs font-semibold text-gray-500">Remediation Plan</span>
                    <p className="text-sm">{threat.remediation_plan}</p>
                  </div>
                </div>
              ))}
              
              <div className="mt-4">
                <Link to="/vulnerabilities" className="text-indigo-600 hover:text-indigo-900">
                  View all vulnerabilities →
                </Link>
              </div>
            </div>
          ) : (
            <p className="text-gray-700">No threats were identified for your technology stack.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default ThreatIntelligence; 