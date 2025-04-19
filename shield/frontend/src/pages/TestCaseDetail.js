import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const TestCaseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [testCase, setTestCase] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  useEffect(() => {
    const fetchTestCaseData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/test-cases/${id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        setTestCase(response.data);
        
        // Fetch vulnerabilities discovered by this test case
        if (response.data.vulnerabilities_ids && response.data.vulnerabilities_ids.length > 0) {
          const vulnResponse = await axios.get(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/vulnerabilities?test_case_id=${id}`,
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          );
          
          setVulnerabilities(vulnResponse.data);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch test case details');
        setLoading(false);
      }
    };

    fetchTestCaseData();
  }, [id]);

  const handleRunTest = async () => {
    setIsRunning(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/test-cases/${id}/run`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      // Update the test case with results
      setTestCase(response.data.test_case);
      
      // Update vulnerabilities if any were found
      if (response.data.vulnerabilities) {
        setVulnerabilities(response.data.vulnerabilities);
      }
      
      setIsRunning(false);
    } catch (err) {
      setError('Failed to run test case');
      setIsRunning(false);
    }
  };

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/test-cases/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      navigate('/test-cases');
    } catch (err) {
      setError('Failed to delete test case');
      setShowConfirmDelete(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Passed':
        return 'bg-green-100 text-green-800';
      case 'Failed':
        return 'bg-red-100 text-red-800';
      case 'In Progress':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const renderRiskLevel = (level) => {
    const colors = {
      'Critical': 'bg-red-100 text-red-800',
      'High': 'bg-orange-100 text-orange-800',
      'Medium': 'bg-yellow-100 text-yellow-800',
      'Low': 'bg-green-100 text-green-800',
      'Info': 'bg-blue-100 text-blue-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[level] || 'bg-gray-100 text-gray-800'}`}>
        {level}
      </span>
    );
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (!testCase) {
    return <div>Test case not found</div>;
  }

  return (
    <div className="container mx-auto px-4">
      <div className="mb-6">
        <Link to="/test-cases" className="text-blue-500 hover:text-blue-700">
          ← Back to Test Cases
        </Link>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">{testCase.name}</h1>
            <div className="flex mt-2 space-x-2">
              <Link to={`/organizations/${testCase.organization_id}`} className="text-blue-600 hover:text-blue-900">
                {testCase.organization_name}
              </Link>
              <span>•</span>
              <span>{testCase.test_type}</span>
              <span>•</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(testCase.status)}`}>
                {testCase.status || 'Pending'}
              </span>
            </div>
          </div>
          
          <div>
            <button 
              onClick={handleRunTest}
              disabled={isRunning}
              className={`${
                isRunning 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-green-500 hover:bg-green-700'
              } text-white font-bold py-2 px-4 rounded mr-2`}
            >
              {isRunning ? 'Running...' : 'Run Test'}
            </button>
            <button 
              onClick={() => setShowConfirmDelete(true)}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Delete
            </button>
          </div>
        </div>
        
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Description</h2>
          <p className="text-gray-700 whitespace-pre-line">{testCase.description}</p>
        </div>
        
        {testCase.parameters && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2">Parameters</h2>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
              {typeof testCase.parameters === 'string' ? testCase.parameters : JSON.stringify(testCase.parameters, null, 2)}
            </pre>
          </div>
        )}
        
        {testCase.result && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2">Results</h2>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
              {typeof testCase.result === 'string' ? testCase.result : JSON.stringify(testCase.result, null, 2)}
            </pre>
          </div>
        )}
        
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-800">Creation Date</h3>
            <p className="text-gray-700">{new Date(testCase.created_at).toLocaleDateString()}</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-800">Last Run</h3>
            <p className="text-gray-700">{testCase.last_run ? new Date(testCase.last_run).toLocaleDateString() : 'Never run'}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-800">Vulnerabilities Found</h3>
            <p className="text-gray-700">{vulnerabilities.length}</p>
          </div>
        </div>
      </div>
      
      {vulnerabilities.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Discovered Vulnerabilities</h2>
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Level
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date Detected
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {vulnerabilities.map((vuln) => (
                  <tr key={vuln.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/vulnerabilities/${vuln.id}`} className="text-blue-600 hover:text-blue-900">
                        {vuln.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {vuln.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {renderRiskLevel(vuln.risk_level)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded text-xs font-medium 
                        ${vuln.status === 'Fixed' ? 'bg-green-100 text-green-800' : 
                          vuln.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' : 
                            'bg-red-100 text-red-800'}`}>
                        {vuln.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(vuln.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {showConfirmDelete && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Confirm Deletion</h2>
            <p className="mb-6">Are you sure you want to delete this test case? This action cannot be undone.</p>
            <div className="flex justify-end space-x-4">
              <button 
                onClick={() => setShowConfirmDelete(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
              >
                Cancel
              </button>
              <button 
                onClick={handleDelete}
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestCaseDetail; 