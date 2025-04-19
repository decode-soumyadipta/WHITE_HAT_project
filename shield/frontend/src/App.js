import React, { useState, useEffect } from 'react';
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
import { AuthProvider } from './utils/AuthContext';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <AuthProvider>
      <div className="flex h-screen bg-gray-100">
        {isLoggedIn && <Sidebar />}
        <div className="flex-1 flex flex-col overflow-hidden">
          {isLoggedIn && <Navbar />}
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4">
            <Routes>
              <Route path="/login" element={!isLoggedIn ? <Login setIsLoggedIn={setIsLoggedIn} /> : <Navigate to="/" />} />
              <Route path="/register" element={!isLoggedIn ? <Register setIsLoggedIn={setIsLoggedIn} /> : <Navigate to="/" />} />
              
              <Route path="/" element={isLoggedIn ? <Dashboard /> : <Navigate to="/login" />} />
              <Route path="/organizations" element={isLoggedIn ? <Organizations /> : <Navigate to="/login" />} />
              <Route path="/organizations/:id" element={isLoggedIn ? <OrganizationDetail /> : <Navigate to="/login" />} />
              <Route path="/vulnerabilities" element={isLoggedIn ? <Vulnerabilities /> : <Navigate to="/login" />} />
              <Route path="/vulnerabilities/:id" element={isLoggedIn ? <VulnerabilityDetail /> : <Navigate to="/login" />} />
              <Route path="/test-cases" element={isLoggedIn ? <TestCases /> : <Navigate to="/login" />} />
              <Route path="/test-cases/:id" element={isLoggedIn ? <TestCaseDetail /> : <Navigate to="/login" />} />
              <Route path="/threat-intelligence" element={isLoggedIn ? <ThreatIntelligence /> : <Navigate to="/login" />} />
              <Route path="/profile" element={isLoggedIn ? <Profile /> : <Navigate to="/login" />} />
              
              {/* Default redirect to login if not logged in */}
              <Route path="*" element={<Navigate to={isLoggedIn ? "/" : "/login"} />} />
            </Routes>
          </main>
        </div>
      </div>
    </AuthProvider>
  );
}

export default App; 