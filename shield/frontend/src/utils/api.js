import axios from 'axios';

// Create an axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Organizations
export const getOrganizations = () => api.get('/organizations');
export const getOrganization = (id) => api.get(`/organizations/${id}`);
export const createOrganization = (data) => api.post('/organizations', data);

// Vulnerabilities
export const getVulnerabilities = (orgId) => 
  api.get('/vulnerabilities', { params: { organization_id: orgId } });
export const getVulnerability = (id) => api.get(`/vulnerabilities/${id}`);
export const createVulnerability = (data) => api.post('/vulnerabilities', data);

// Test Cases
export const getTestCases = (params) => api.get('/test-cases', { params });
export const getTestCase = (id) => api.get(`/test-cases/${id}`);
export const createTestCase = (data) => api.post('/test-cases', data);

// AI Services
export const analyzeThreat = (data) => api.post('/analyze-threats', data);
export const generateTestCases = (data) => api.post('/generate-test-cases', data);
export const simulateAttack = (data) => api.post('/simulate-attack', data);
export const analyzeRisk = (data) => api.post('/analyze-risk', data);

// Dashboard
export const getDashboardData = (orgId) => 
  api.get('/dashboard-data', { params: { organization_id: orgId } });

export default api;