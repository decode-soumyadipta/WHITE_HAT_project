import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import Login from './pages/Login';
import Layout from './components/Layout/Layout';
import Profile from './pages/Profile';

// Modified ProtectedRoute to bypass authentication completely
const ProtectedRoute = ({ children }) => {
  // Always render the children without any authentication checks
  return children;
};

function App() {
  return (
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
  );
}

export default App; 