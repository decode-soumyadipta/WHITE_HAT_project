import React, { createContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [githubRepos, setGithubRepos] = useState([]);
  const [githubLoading, setGithubLoading] = useState(false);

  const fetchUserProfile = useCallback(async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/profile`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setUser(response.data);
    } catch (err) {
      console.error('Error fetching profile:', err);
      logout();
      setError(err.response?.data?.message || 'Failed to fetch user profile');
    } finally {
      setLoading(false);
    }
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
  }, [token, fetchUserProfile]);

  useEffect(() => {
    // Check URL for GitHub callback parameters
    const urlParams = new URLSearchParams(window.location.search);
    const githubConnected = urlParams.get('github_connected');
    const newToken = urlParams.get('token');
    
    if (githubConnected === 'true' && newToken) {
      // Update token and clear URL parameters
      localStorage.setItem('token', newToken);
      setToken(newToken);
      
      // Remove query parameters from URL without refreshing
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // Add updateUser function
  const updateUser = (userData) => {
    setUser(userData);
  };

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/login`, { email, password });
      const { token: authToken, user: userData } = response.data;
      
      // Store token and user data
      localStorage.setItem('token', authToken);
      setToken(authToken);
      setUser(userData);
      return true;
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.message || 'Failed to login');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/register`, userData);
      return true;
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.message || 'Failed to register');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = useCallback(() => {
    // Clear token and user data
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setGithubRepos([]);
    setError(null);
  }, []);

  const fetchGithubRepositories = async () => {
    if (!token) return [];
    
    setGithubLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/github/repositories`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setGithubRepos(response.data.repositories);
      return response.data.repositories;
    } catch (err) {
      console.error('GitHub repositories error:', err);
      setError(err.response?.data?.message || 'Failed to fetch GitHub repositories');
      return [];
    } finally {
      setGithubLoading(false);
    }
  };

  const connectToGithub = async () => {
    if (!token) return false;
    
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/github`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Redirect to GitHub authorization page
      window.location.href = response.data.auth_url;
      return true;
    } catch (err) {
      console.error('GitHub connection error:', err);
      setError(err.response?.data?.message || 'Failed to connect to GitHub');
      return false;
    }
  };
  
  const disconnectFromGithub = async () => {
    if (!token) return false;
    
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/github/disconnect`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Update user data after disconnection
      await fetchUserProfile();
      setGithubRepos([]);
      return true;
    } catch (err) {
      console.error('GitHub disconnection error:', err);
      setError(err.response?.data?.message || 'Failed to disconnect from GitHub');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        error,
        githubRepos,
        githubLoading,
        login,
        register,
        logout,
        fetchUserProfile,
        updateUser,
        connectToGithub,
        disconnectFromGithub,
        fetchGithubRepositories
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 