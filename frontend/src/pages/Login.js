import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../Mobile.css';
import '../EnhancedAnimations.css';
import AnimatedBackground from '../components/AnimatedBackground';
import LoadingSpinner from '../components/LoadingSpinner';
import AnimatedCard from '../components/AnimatedCard';
import GlowingButton from '../components/GlowingButton';

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
      <AnimatedBackground />
      <div className="mobile-container">
        <div className="mobile-header">
          <div className="mobile-header-content">
            <h1 className="animated-title">🚀 GrabHack</h1>
            <p>AI-Powered Customer Service Platform</p>
          </div>
        </div>

        <AnimatedCard>
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

            <GlowingButton
              type="submit"
              disabled={loading || !credentials.username || !credentials.password}
              variant="primary"
              size="large"
              glowColor="#00C851"
              style={{ 
                width: '100%',
                background: 'linear-gradient(135deg, #00C851 0%, #00A043 50%, #007B33 100%)',
                fontSize: '18px',
                fontWeight: '700',
                padding: '16px 24px',
                borderRadius: '16px',
                boxShadow: loading ? 'none' : '0 8px 32px rgba(0, 200, 81, 0.4), 0 0 0 1px rgba(0, 200, 81, 0.2)',
                transition: 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                transform: loading ? 'scale(0.98)' : 'scale(1)',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
                  <div style={{
                    width: '20px',
                    height: '20px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTop: '2px solid white',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}></div>
                  <span>Signing In...</span>
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <span>🔐</span>
                  <span>Sign In</span>
                  <span>✨</span>
                </div>
              )}
            </GlowingButton>
          </form>
        </AnimatedCard>
      </div>
    </div>
  );
};

export default Login;