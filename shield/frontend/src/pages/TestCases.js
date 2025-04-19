import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const TestCases = () => {
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [organizations, setOrganizations] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState('');
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [generateFormData, setGenerateFormData] = useState({
    organization_id: '',
    name: '',
    description: '',
    test_type: 'Penetration Test',
    parameters: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // Fetch test cases
        const testCasesResponse = await axios.get(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/test-cases`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        setTestCases(testCasesResponse.data);
        
        // Fetch organizations for filter and form
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
        setError('Failed to fetch test cases');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleOrgChange = (e) => {
    setSelectedOrg(e.target.value);
  };

  const handleGenerateInputChange = (e) => {
    setGenerateFormData({
      ...generateFormData,
      [e.target.name]: e.target.value
    });
  };

  const handleGenerateSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/test-cases`,
        generateFormData,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      // Reset form and refresh test cases
      setGenerateFormData({
        organization_id: '',
        name: '',
        description: '',
        test_type: 'Penetration Test',
        parameters: ''
      });
      setShowGenerateForm(false);
      
      // Fetch updated test cases
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/test-cases`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      setTestCases(response.data);
    } catch (err) {
      setError('Failed to generate test case');
    }
  };

  const filteredTestCases = selectedOrg 
    ? testCases.filter(tc => tc.organization_id === parseInt(selectedOrg))
    : testCases;

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

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Test Cases</h1>
        <button
          onClick={() => setShowGenerateForm(!showGenerateForm)}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          {showGenerateForm ? 'Cancel' : 'Generate Test Case'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {showGenerateForm && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Generate New Test Case</h2>
          <form onSubmit={handleGenerateSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="organization_id">
                  Organization
                </label>
                <select
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="organization_id"
                  name="organization_id"
                  value={generateFormData.organization_id}
                  onChange={handleGenerateInputChange}
                  required
                >
                  <option value="">Select Organization</option>
                  {organizations.map(org => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="test_type">
                  Test Type
                </label>
                <select
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="test_type"
                  name="test_type"
                  value={generateFormData.test_type}
                  onChange={handleGenerateInputChange}
                  required
                >
                  <option value="Penetration Test">Penetration Test</option>
                  <option value="Vulnerability Scan">Vulnerability Scan</option>
                  <option value="Code Review">Code Review</option>
                  <option value="Social Engineering">Social Engineering</option>
                  <option value="Configuration Audit">Configuration Audit</option>
                </select>
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
                Test Case Name
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="name"
                type="text"
                name="name"
                placeholder="Enter test case name"
                value={generateFormData.name}
                onChange={handleGenerateInputChange}
                required
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                Description
              </label>
              <textarea
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="description"
                name="description"
                placeholder="Enter test case description"
                value={generateFormData.description}
                onChange={handleGenerateInputChange}
                rows="3"
                required
              ></textarea>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="parameters">
                Parameters (Optional)
              </label>
              <textarea
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="parameters"
                name="parameters"
                placeholder="Enter parameters in JSON format or key:value pairs"
                value={generateFormData.parameters}
                onChange={handleGenerateInputChange}
                rows="3"
              ></textarea>
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Generate Test Case
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-gray-700 font-bold" htmlFor="orgFilter">
            Filter by Organization:
          </label>
          <select
            id="orgFilter"
            value={selectedOrg}
            onChange={handleOrgChange}
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          >
            <option value="">All Organizations</option>
            {organizations.map(org => (
              <option key={org.id} value={org.id}>{org.name}</option>
            ))}
          </select>
        </div>
      </div>

      {filteredTestCases.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTestCases.map(testCase => (
            <Link 
              key={testCase.id} 
              to={`/test-cases/${testCase.id}`}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
            >
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">{testCase.name}</h2>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(testCase.status)}`}>
                    {testCase.status || 'Pending'}
                  </span>
                </div>
                <p className="text-gray-600 mb-4">{testCase.organization_name}</p>
                <p className="text-gray-700 mb-4 line-clamp-2">{testCase.description}</p>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Type: {testCase.test_type}</span>
                  <span className="text-gray-500">
                    {testCase.created_at ? new Date(testCase.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
              <div className="bg-gray-50 px-6 py-3">
                <div className="text-right">
                  <span className="text-blue-500 font-medium">View Details →</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <p className="text-gray-600">No test cases found.</p>
          <button
            onClick={() => setShowGenerateForm(true)}
            className="text-blue-500 hover:text-blue-700 mt-2"
          >
            Generate your first test case
          </button>
        </div>
      )}
    </div>
  );
};

export default TestCases; 