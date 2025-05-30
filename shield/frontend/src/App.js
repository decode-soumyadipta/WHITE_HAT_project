import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './components/Dashboard/Dashboard';
import Login from './pages/Login';
import Layout from './components/Layout/Layout';
import Profile from './pages/Profile';
import GitHubAnalyzer from './pages/GitHubAnalyzer';
import AIAgentAutomation from './pages/AIAgentAutomation';

// Modified ProtectedRoute to bypass authentication completely
const ProtectedRoute = ({ children }) => {
  // Always render the children without any authentication checks
  return children;
};

function App() {
  return (
    <>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#333',
            color: '#fff',
          },
          success: {
            style: {
              background: '#22c55e',
              color: '#fff',
            },
          },
          error: {
            style: {
              background: '#ef4444',
              color: '#fff',
            },
          },
        }}
      />
      <Routes>
        {/* Default route redirects to login */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/github-analyzer"
          element={
            <ProtectedRoute>
              <Layout>
                <GitHubAnalyzer />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-agent-automation"
          element={
            <ProtectedRoute>
              <Layout>
                <AIAgentAutomation />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Add routes for other navigation items */}
        <Route
          path="/vulnerabilities"
          element={
            <ProtectedRoute>
              <Layout>
                <div className="p-4">
                  <h1 className="text-2xl font-bold">Vulnerabilities</h1>
                  <p>This page is under construction.</p>
                </div>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/test-cases"
          element={
            <ProtectedRoute>
              <Layout>
                <div className="p-4">
                  <h1 className="text-2xl font-bold">Test Cases</h1>
                  <p>This page is under construction.</p>
                </div>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <div className="p-4">
                  <h1 className="text-2xl font-bold">Settings</h1>
                  <p>This page is under construction.</p>
                </div>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App; 