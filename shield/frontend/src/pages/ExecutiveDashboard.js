import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Chart as ChartJS, 
  ArcElement, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  PointElement,
  LineElement,
  Title, 
  Tooltip, 
  Legend,
  RadialLinearScale,
  Filler
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import '../styles/ExecutiveDashboard.css';

// Register ChartJS components
ChartJS.register(
  ArcElement, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  PointElement,
  LineElement,
  Title, 
  Tooltip, 
  Legend,
  RadialLinearScale,
  Filler
);

const ExecutiveDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d');
  const [selectedRiskType, setSelectedRiskType] = useState('all');

  // Mock data - would be replaced with actual API calls
  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDashboardData({
        metrics: {
          totalVulnerabilities: 147,
          criticalVulnerabilities: 12,
          highRiskAssets: 8,
          averageTimeToRemediate: 3.2,
          securityScore: 68,
          financialImpact: 342500
        },
        vulnerabilityTrends: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [
            {
              label: 'Critical',
              data: [5, 8, 12, 9, 12, 8],
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
            },
            {
              label: 'High',
              data: [15, 19, 17, 14, 22, 18],
              borderColor: '#F97316',
              backgroundColor: 'rgba(249, 115, 22, 0.1)',
            },
            {
              label: 'Medium',
              data: [25, 29, 32, 24, 26, 28],
              borderColor: '#F59E0B',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
            },
            {
              label: 'Low',
              data: [42, 38, 35, 30, 36, 41],
              borderColor: '#10B981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
            }
          ]
        },
        techStackRisks: {
          labels: ['Kubernetes', 'Python', 'Node.js', 'React', 'PostgreSQL', 'Docker'],
          datasets: [{
            label: 'Risk Score',
            data: [75, 45, 60, 30, 55, 80],
            backgroundColor: 'rgba(99, 102, 241, 0.7)',
            borderColor: '#6366F1',
            borderWidth: 1
          }]
        },
        recentVulnerabilities: [
          {
            id: 1,
            title: 'Kubernetes API Server RBAC Bypass',
            severity: 'critical',
            cvssScore: 9.8,
            affectedAssets: 12,
            estimatedImpact: 85000,
            status: 'Open',
            discoveredAt: '2023-11-05'
          },
          {
            id: 2,
            title: 'Node.js Command Injection Vulnerability',
            severity: 'high',
            cvssScore: 8.2,
            affectedAssets: 8,
            estimatedImpact: 45000,
            status: 'In Progress',
            discoveredAt: '2023-11-08'
          },
          {
            id: 3,
            title: 'Docker Container Escape',
            severity: 'critical',
            cvssScore: 9.1,
            affectedAssets: 6,
            estimatedImpact: 120000,
            status: 'Open',
            discoveredAt: '2023-11-10'
          },
          {
            id: 4,
            title: 'PostgreSQL Privilege Escalation',
            severity: 'medium',
            cvssScore: 6.5,
            affectedAssets: 3,
            estimatedImpact: 25000,
            status: 'Resolved',
            discoveredAt: '2023-10-30'
          }
        ],
        testCaseResults: {
          totalTests: 86,
          passedTests: 63,
          failedTests: 23,
          byCategory: {
            'Infrastructure': { passed: 18, failed: 7 },
            'Application': { passed: 25, failed: 10 },
            'Data Security': { passed: 12, failed: 4 },
            'Access Control': { passed: 8, failed: 2 }
          }
        },
        threatIntelligence: [
          {
            id: 1,
            threat: 'Advanced Persistent Threat',
            relevance: 'high',
            targetedTech: ['Kubernetes', 'Docker'],
            detectedActivity: true,
            recommendedActions: 2
          },
          {
            id: 2,
            threat: 'Supply Chain Attack',
            relevance: 'medium',
            targetedTech: ['Node.js', 'npm packages'],
            detectedActivity: false,
            recommendedActions: 3
          },
          {
            id: 3,
            threat: 'Data Exfiltration Campaign',
            relevance: 'high',
            targetedTech: ['PostgreSQL', 'APIs'],
            detectedActivity: true,
            recommendedActions: 4
          }
        ]
      });
      setLoading(false);
    }, 1500);
  }, []);

  const getRiskTagClass = (severity) => {
    switch(severity) {
      case 'critical': return 'risk-critical';
      case 'high': return 'risk-high';
      case 'medium': return 'risk-medium';
      case 'low': return 'risk-low';
      default: return 'risk-low';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <div style={{ fontSize: '18px', fontWeight: 500, marginBottom: '8px' }}>
            Loading executive dashboard...
          </div>
          <div>Gathering security insights and metrics</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Executive Security Dashboard</h1>
          <p className="dashboard-subtitle">
            Comprehensive overview of your organization's security posture
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <select 
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <button className="action-button">
            Generate Report
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="dashboard-metrics">
        <div className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Total Vulnerabilities</h3>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <p className="metric-value">{dashboardData.metrics.totalVulnerabilities}</p>
          <div className="metric-change negative">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
            <span>12% from last period</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Critical Issues</h3>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <p className="metric-value">{dashboardData.metrics.criticalVulnerabilities}</p>
          <div className="metric-change negative">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
            <span>3 new since last week</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Security Score</h3>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <p className="metric-value">{dashboardData.metrics.securityScore}%</p>
          <div className="metric-change positive">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
            <span>5% from last month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <h3 className="metric-title">Estimated Financial Impact</h3>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="1" x2="12" y2="23"></line>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <p className="metric-value">${dashboardData.metrics.financialImpact.toLocaleString()}</p>
          <div className="metric-change negative">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
            <span>$68K increase in risk</span>
          </div>
        </div>
      </div>

      {/* Charts and Data Visualization */}
      <div className="dashboard-row">
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h2 className="dashboard-card-title">Vulnerability Trends</h2>
            <div className="dashboard-card-actions">
              <select 
                value={selectedRiskType}
                onChange={(e) => setSelectedRiskType(e.target.value)}
                style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '13px' }}
              >
                <option value="all">All Types</option>
                <option value="critical">Critical Only</option>
                <option value="high">High & Critical</option>
              </select>
            </div>
          </div>
          <div className="chart-container">
            <Line 
              data={dashboardData.vulnerabilityTrends}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                tension: 0.3,
                plugins: {
                  legend: {
                    position: 'bottom',
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Number of Vulnerabilities'
                    }
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Month'
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h2 className="dashboard-card-title">Technology Stack Risk Assessment</h2>
            <div className="dashboard-card-actions">
              <button style={{ border: 'none', background: 'none', cursor: 'pointer' }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="1"></circle>
                  <circle cx="19" cy="12" r="1"></circle>
                  <circle cx="5" cy="12" r="1"></circle>
                </svg>
              </button>
            </div>
          </div>
          <div className="chart-container">
            <Bar 
              data={dashboardData.techStackRisks}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                  legend: {
                    display: false,
                  },
                  tooltip: {
                    callbacks: {
                      label: function(context) {
                        const value = context.raw;
                        let risk = 'Low Risk';
                        if (value >= 75) risk = 'Critical Risk';
                        else if (value >= 60) risk = 'High Risk';
                        else if (value >= 40) risk = 'Medium Risk';
                        return `Risk Score: ${value} - ${risk}`;
                      }
                    }
                  }
                },
                scales: {
                  x: {
                    max: 100,
                    title: {
                      display: true,
                      text: 'Risk Score'
                    },
                    grid: {
                      display: false
                    }
                  },
                  y: {
                    grid: {
                      display: false
                    }
                  }
                }
              }}
            />
          </div>
          <div className="tech-stack-list">
            {dashboardData.techStackRisks.labels.map((tech, index) => (
              <div key={tech} className="tech-item">
                {tech}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Vulnerability Table */}
      <div className="dashboard-card">
        <div className="dashboard-card-header">
          <h2 className="dashboard-card-title">High Impact Vulnerabilities</h2>
          <Link to="/vulnerabilities" style={{ fontSize: '14px', color: '#2563EB', textDecoration: 'none' }}>
            View All →
          </Link>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="vuln-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Severity</th>
                <th>CVSS Score</th>
                <th>Affected Assets</th>
                <th>Est. Financial Impact</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.recentVulnerabilities.map(vuln => (
                <tr key={vuln.id}>
                  <td>
                    <Link to={`/vulnerabilities/${vuln.id}`} style={{ color: '#2563EB', textDecoration: 'none' }}>
                      {vuln.title}
                    </Link>
                  </td>
                  <td>
                    <span className={`risk-tag ${getRiskTagClass(vuln.severity)}`}>
                      {vuln.severity.charAt(0).toUpperCase() + vuln.severity.slice(1)}
                    </span>
                  </td>
                  <td>{vuln.cvssScore}</td>
                  <td>{vuln.affectedAssets}</td>
                  <td>${vuln.estimatedImpact.toLocaleString()}</td>
                  <td>{vuln.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Test Case Results & Threat Intelligence */}
      <div className="dashboard-row">
        {/* Test Case Results */}
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h2 className="dashboard-card-title">Security Testing Results</h2>
            <Link to="/test-cases" style={{ fontSize: '14px', color: '#2563EB', textDecoration: 'none' }}>
              View Details →
            </Link>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '14px', color: '#666', margin: '0 0 5px 0' }}>Total Tests</p>
              <p style={{ fontSize: '28px', fontWeight: '600', margin: '0' }}>{dashboardData.testCaseResults.totalTests}</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '14px', color: '#666', margin: '0 0 5px 0' }}>Passed</p>
              <p style={{ fontSize: '28px', fontWeight: '600', color: '#10B981', margin: '0' }}>{dashboardData.testCaseResults.passedTests}</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '14px', color: '#666', margin: '0 0 5px 0' }}>Failed</p>
              <p style={{ fontSize: '28px', fontWeight: '600', color: '#EF4444', margin: '0' }}>{dashboardData.testCaseResults.failedTests}</p>
            </div>
          </div>
          {/* Test categories */}
          {Object.entries(dashboardData.testCaseResults.byCategory).map(([category, results]) => (
            <div key={category} style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '14px' }}>{category}</span>
                <span style={{ fontSize: '14px' }}>{Math.round((results.passed / (results.passed + results.failed)) * 100)}% Pass Rate</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill fill-low" 
                  style={{ width: `${(results.passed / (results.passed + results.failed)) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: '20px' }}>
            <button className="action-button">
              Run Infrastructure Tests
            </button>
          </div>
        </div>

        {/* Threat Intelligence */}
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h2 className="dashboard-card-title">Threat Intelligence</h2>
            <Link to="/threat-intelligence" style={{ fontSize: '14px', color: '#2563EB', textDecoration: 'none' }}>
              View All →
            </Link>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <p style={{ fontSize: '15px', margin: '0 0 12px 0' }}>Active threats targeting your tech stack:</p>
            {dashboardData.threatIntelligence.map(threat => (
              <div key={threat.id} style={{ padding: '12px', borderLeft: `3px solid ${threat.relevance === 'high' ? '#EF4444' : '#F59E0B'}`, background: '#f9f9f9', marginBottom: '12px', borderRadius: '0 4px 4px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ fontSize: '16px', margin: '0', fontWeight: '500' }}>{threat.threat}</h3>
                  <span className={`risk-tag ${threat.relevance === 'high' ? 'risk-critical' : 'risk-medium'}`}>{threat.relevance === 'high' ? 'High Relevance' : 'Medium Relevance'}</span>
                </div>
                <p style={{ fontSize: '14px', margin: '8px 0', color: '#666' }}>
                  Targeting: {threat.targetedTech.join(', ')}
                </p>
                {threat.detectedActivity && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#EF4444', fontSize: '14px', fontWeight: '500' }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="8" x2="12" y2="12"></line>
                      <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    Activity detected in your environment
                  </div>
                )}
                <div style={{ marginTop: '8px' }}>
                  <Link to={`/threat-intelligence/${threat.id}`} style={{ color: '#2563EB', textDecoration: 'none', fontSize: '14px' }}>
                    View {threat.recommendedActions} recommended actions →
                  </Link>
                </div>
              </div>
            ))}
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <button className="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 16v-4"></path>
                <path d="M12 8h.01"></path>
              </svg>
              Get Threat Alerts
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveDashboard; 