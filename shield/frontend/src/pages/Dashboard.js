import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../utils/AuthContext';
import { getDashboardData } from '../utils/api';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);

  useEffect(() => {
    if (user && user.organization_id) {
      setSelectedOrg(user.organization_id);
      fetchDashboardData(user.organization_id);
    }
  }, [user]);

  const fetchDashboardData = async (orgId) => {
    setLoading(true);
    try {
      const response = await getDashboardData(orgId);
      setDashboardData(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please try again later.');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="text-xl font-semibold">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <p>{error}</p>
      </div>
    );
  }

  if (!selectedOrg) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
        <p>Please select or create an organization to view the dashboard.</p>
        <Link to="/organizations" className="text-blue-600 hover:underline mt-2 inline-block">
          Go to Organizations
        </Link>
      </div>
    );
  }

  // Prepare chart data if dashboard data is available
  const vulnerabilityByServerityData = dashboardData ? {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [
      {
        label: 'Vulnerabilities by Severity',
        data: [
          dashboardData.vulnerability_by_severity.critical || 0,
          dashboardData.vulnerability_by_severity.high || 0,
          dashboardData.vulnerability_by_severity.medium || 0,
          dashboardData.vulnerability_by_severity.low || 0
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.7)',
          'rgba(249, 115, 22, 0.7)',
          'rgba(245, 158, 11, 0.7)',
          'rgba(16, 185, 129, 0.7)'
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(249, 115, 22, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(16, 185, 129, 1)'
        ],
        borderWidth: 1,
      },
    ],
  } : null;

  const testCaseStatsData = dashboardData ? {
    labels: ['Pending', 'Running', 'Completed', 'Failed'],
    datasets: [
      {
        label: 'Test Case Status',
        data: [
          dashboardData.test_case_stats.pending || 0,
          dashboardData.test_case_stats.running || 0,
          dashboardData.test_case_stats.completed || 0,
          dashboardData.test_case_stats.failed || 0
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.7)',
          'rgba(139, 92, 246, 0.7)',
          'rgba(16, 185, 129, 0.7)',
          'rgba(239, 68, 68, 0.7)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 1,
      },
    ],
  } : null;

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold mb-6">Security Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-2">Total Vulnerabilities</h2>
          <p className="text-4xl font-bold text-indigo-600">
            {dashboardData ? 
              Object.values(dashboardData.vulnerability_by_severity).reduce((a, b) => a + b, 0) : 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-2">Test Cases</h2>
          <p className="text-4xl font-bold text-green-600">
            {dashboardData ? dashboardData.test_case_stats.total : 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-2">Critical Issues</h2>
          <p className="text-4xl font-bold text-red-600">
            {dashboardData ? dashboardData.vulnerability_by_severity.critical || 0 : 0}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Vulnerabilities by Severity</h2>
          {vulnerabilityByServerityData && (
            <div className="h-64">
              <Pie data={vulnerabilityByServerityData} />
            </div>
          )}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Test Case Status</h2>
          {testCaseStatsData && (
            <div className="h-64">
              <Bar 
                data={testCaseStatsData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        precision: 0
                      }
                    }
                  }
                }}
              />
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-xl font-semibold mb-4">Recent Vulnerabilities</h2>
        {dashboardData && dashboardData.recent_vulnerabilities.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CVSS Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Discovered</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dashboardData.recent_vulnerabilities.map((vuln) => (
                  <tr key={vuln.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/vulnerabilities/${vuln.id}`} className="text-indigo-600 hover:text-indigo-900">
                        {vuln.title}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium severity-${vuln.severity}`}>
                        {vuln.severity.charAt(0).toUpperCase() + vuln.severity.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{vuln.cvss_score || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{vuln.status}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{new Date(vuln.discovered_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No recent vulnerabilities found.</p>
        )}
        <div className="mt-4">
          <Link to="/vulnerabilities" className="text-indigo-600 hover:text-indigo-900">
            View all vulnerabilities →
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Threat Intelligence Analysis</h2>
          <p className="text-gray-700 mb-4">
            Run a threat intelligence analysis to identify emerging threats relevant to your technology stack.
          </p>
          <Link to="/threat-intelligence" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
            Run Analysis
          </Link>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Security Test Cases</h2>
          <p className="text-gray-700 mb-4">
            Generate and manage penetration testing scenarios based on your infrastructure.
          </p>
          <Link to="/test-cases" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
            View Test Cases
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 