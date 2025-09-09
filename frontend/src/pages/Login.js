import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../Mobile.css';

const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/login', {
        username: credentials.username,
        password: credentials.password
      });

      if (response.data.success) {
        const userData = response.data.user;
        localStorage.setItem('user', JSON.stringify({
          id: userData.id,
          type: userData.user_type,
          username: userData.username,
          credibility_score: userData.credibility_score,
          services: userData.services
        }));
        navigate('/dashboard');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Invalid username or password');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <div className="mobile-container">
        <div className="mobile-header">
          <h1>🚀 GrabHack</h1>
          <p>AI-Powered Customer Service Platform</p>
        </div>

        <div className="mobile-card">
          <h2 style={{ textAlign: 'center', marginBottom: '24px', fontSize: '28px', fontWeight: '700', color: '#333' }}>
            Welcome Back
          </h2>
          <p style={{ textAlign: 'center', marginBottom: '32px', color: '#6c757d' }}>
            Sign in to your account
          </p>

          {error && <div className="mobile-error-message">{error}</div>}

          <form onSubmit={handleLogin}>
            <div className="mobile-form-group">
              <label className="mobile-form-label">Username</label>
              <input
                type="text"
                className="mobile-form-input"
                placeholder="Enter your username"
                value={credentials.username}
                onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                required
                autoComplete="username"
              />
            </div>

            <div className="mobile-form-group">
              <label className="mobile-form-label">Password</label>
              <input
                type="password"
                className="mobile-form-input"
                placeholder="Enter your password"
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                required
                autoComplete="current-password"
              />
            </div>

            <button 
              type="submit" 
              className="mobile-btn mobile-btn-primary"
              disabled={loading || !credentials.username || !credentials.password}
            >
              {loading ? (
                <>
                  <div className="mobile-spinner" style={{ width: '20px', height: '20px', marginRight: '8px' }}></div>
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;