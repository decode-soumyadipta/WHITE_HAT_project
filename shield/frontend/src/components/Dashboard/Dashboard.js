import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/dashboard/overview');
        setDashboardData(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const trendData = {
    labels: Object.keys(dashboardData.trends),
    datasets: [
      {
        label: 'Critical',
        data: Object.values(dashboardData.trends).map(day => day.critical),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
      {
        label: 'High',
        data: Object.values(dashboardData.trends).map(day => day.high),
        borderColor: 'rgb(255, 159, 64)',
        tension: 0.1,
      },
      {
        label: 'Medium',
        data: Object.values(dashboardData.trends).map(day => day.medium),
        borderColor: 'rgb(255, 205, 86)',
        tension: 0.1,
      },
      {
        label: 'Low',
        data: Object.values(dashboardData.trends).map(day => day.low),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Security Dashboard</h1>
        <div className="text-right">
          <div className="text-4xl font-bold text-blue-600">{dashboardData.risk_score}%</div>
          <div className="text-sm text-gray-500">Security Score</div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Vulnerability Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Vulnerabilities</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-red-600">Critical</span>
              <span className="font-bold">{dashboardData.vulnerability_stats.critical}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-500">High</span>
              <span className="font-bold">{dashboardData.vulnerability_stats.high}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-yellow-500">Medium</span>
              <span className="font-bold">{dashboardData.vulnerability_stats.medium}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-500">Low</span>
              <span className="font-bold">{dashboardData.vulnerability_stats.low}</span>
            </div>
          </div>
        </div>

        {/* Test Case Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Test Cases</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Total</span>
              <span className="font-bold">{dashboardData.test_case_stats.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-500">Passed</span>
              <span className="font-bold">{dashboardData.test_case_stats.passed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-500">Failed</span>
              <span className="font-bold">{dashboardData.test_case_stats.failed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-yellow-500">Pending</span>
              <span className="font-bold">{dashboardData.test_case_stats.pending}</span>
            </div>
          </div>
        </div>

        {/* Recent Vulnerabilities */}
        <div className="bg-white rounded-lg shadow p-6 col-span-2">
          <h3 className="text-lg font-semibold mb-4">Recent Vulnerabilities</h3>
          <div className="space-y-4">
            {dashboardData.recent_vulnerabilities.map((vuln) => (
              <div key={vuln.id} className="border-b pb-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{vuln.title}</h4>
                    <p className="text-sm text-gray-600">{vuln.description}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    vuln.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    vuln.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    vuln.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {vuln.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Vulnerability Trends</h3>
        <div className="h-96">
          <Line
            data={trendData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1
                  }
                }
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 