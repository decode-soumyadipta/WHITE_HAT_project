import React, { useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Organizations from './pages/Organizations';
import OrganizationDetail from './pages/OrganizationDetail';
import Vulnerabilities from './pages/Vulnerabilities';
import VulnerabilityDetail from './pages/VulnerabilityDetail';
import TestCases from './pages/TestCases';
import TestCaseDetail from './pages/TestCaseDetail';
import ThreatIntelligence from './pages/ThreatIntelligence';
import Profile from './pages/Profile';

// Context
import AuthContext, { AuthProvider } from './utils/AuthContext';

function AppContent() {
  const { token, loading } = useContext(AuthContext);
  
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {token && <Sidebar />}
      <div className="flex-1 flex flex-col overflow-hidden">
        {token && <Navbar />}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4">
          <Routes>
            <Route path="/login" element={!token ? <Login /> : <Navigate to="/" />} />
            <Route path="/register" element={!token ? <Register /> : <Navigate to="/" />} />
            
            <Route path="/" element={token ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/organizations" element={token ? <Organizations /> : <Navigate to="/login" />} />
            <Route path="/organizations/:id" element={token ? <OrganizationDetail /> : <Navigate to="/login" />} />
            <Route path="/vulnerabilities" element={token ? <Vulnerabilities /> : <Navigate to="/login" />} />
            <Route path="/vulnerabilities/:id" element={token ? <VulnerabilityDetail /> : <Navigate to="/login" />} />
            <Route path="/test-cases" element={token ? <TestCases /> : <Navigate to="/login" />} />
            <Route path="/test-cases/:id" element={token ? <TestCaseDetail /> : <Navigate to="/login" />} />
            <Route path="/threat-intelligence" element={token ? <ThreatIntelligence /> : <Navigate to="/login" />} />
            <Route path="/profile" element={token ? <Profile /> : <Navigate to="/login" />} />
            
            {/* Default redirect to login if not logged in */}
            <Route path="*" element={<Navigate to={token ? "/" : "/login"} />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App; 