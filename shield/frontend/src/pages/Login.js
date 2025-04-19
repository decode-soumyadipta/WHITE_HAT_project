import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthContext from '../utils/AuthContext';
import '../styles/Login.css';

function Login({ setIsLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setFormError('');
    setLoading(true);
    
    try {
      await login(email, password);
      setIsLoggedIn(true);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Failed to login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="background-image" style={{ backgroundImage: `url('https://thumbs.dreamstime.com/b/abstract-cybersecurity-concept-design-dark-background-green-tones-generated-ai-abstract-cybersecurity-concept-design-dark-352765010.jpg')` }}></div>
      <div className="binary-overlay"></div>
      <div className="shield-overlay"></div>
      
      <div className="login-card">
        <div className="login-header">
          <h2 className="login-title">SHIELD</h2>
          <p className="login-subtitle">
            Synthetic Hacking Intelligence for Enhanced Liability Defense
          </p>
        </div>
        
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="email-address" className="sr-only">Email address</label>
            <input
              id="email-address"
              name="email"
              type="email"
              autoComplete="email"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-800 focus:border-green-800 focus:z-10 sm:text-sm"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="password" className="sr-only">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-800 focus:border-green-800 focus:z-10 sm:text-sm"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {(formError || error) && (
            <div className="login-error">
              {formError || error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="login-button"
            >
              Sign in
            </button>
          </div>
          
          <div className="login-link">
            <Link to="/register">
              Don't have an account? Register
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login; 