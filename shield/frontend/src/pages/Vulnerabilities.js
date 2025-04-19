import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Vulnerabilities = () => {
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    riskLevel: '',
    status: '',
    organization: ''
  });
  const [organizations, setOrganizations] = useState([]);

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
        
        // Fetch organizations for filter dropdown
        const orgResponse = await axios.get(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/organizations`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        setOrganizations(orgResponse.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch vulnerabilities');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const filteredVulnerabilities = vulnerabilities.filter(vuln => {
    return (
      (filters.riskLevel === '' || vuln.risk_level === filters.riskLevel) &&
      (filters.status === '' || vuln.status === filters.status) &&
      (filters.organization === '' || vuln.organization_id === parseInt(filters.organization))
    );
  });

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

  return (
    <div className="container mx-auto px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Vulnerabilities</h1>
        <Link to="/vulnerabilities/new" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Add Vulnerability
        </Link>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="riskLevel">
              Risk Level
            </label>
            <select
              id="riskLevel"
              name="riskLevel"
              value={filters.riskLevel}
              onChange={handleFilterChange}
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">All Risk Levels</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
              <option value="Info">Info</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="status">
              Status
            </label>
            <select
              id="status"
              name="status"
              value={filters.status}
              onChange={handleFilterChange}
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">All Statuses</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Fixed">Fixed</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="organization">
              Organization
            </label>
            <select
              id="organization"
              name="organization"
              value={filters.organization}
              onChange={handleFilterChange}
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">All Organizations</option>
              {organizations.map(org => (
                <option key={org.id} value={org.id}>{org.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {filteredVulnerabilities.length > 0 ? (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Organization
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
              {filteredVulnerabilities.map((vuln) => (
                <tr key={vuln.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/vulnerabilities/${vuln.id}`} className="text-blue-600 hover:text-blue-900">
                      {vuln.name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/organizations/${vuln.organization_id}`} className="text-blue-600 hover:text-blue-900">
                      {vuln.organization_name}
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
      ) : (
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <p className="text-gray-600">No vulnerabilities found with the selected filters.</p>
          <Link to="/vulnerabilities/new" className="text-blue-500 hover:text-blue-700 mt-2 inline-block">
            Add a new vulnerability
          </Link>
        </div>
      )}
    </div>
  );
};

export default Vulnerabilities; 