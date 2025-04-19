import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load user data if token exists
    if (token) {
      fetchUserProfile();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/profile`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setUser(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching profile:', err);
      logout();
      setLoading(false);
    }
  };

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
      setLoading(false);
      return true;
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.message || 'Failed to login');
      setLoading(false);
      return false;
    }
  };

  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/auth/register`, userData);
      setLoading(false);
      return true;
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.message || 'Failed to register');
      setLoading(false);
      return false;
    }
  };

  const logout = () => {
    // Clear token and user data
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        error,
        login,
        register,
        logout,
        fetchUserProfile,
        updateUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 