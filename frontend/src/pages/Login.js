import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Login = () => {
  const [userType, setUserType] = useState('');
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const userTypes = [
    { id: 'customer', name: 'Customer', services: ['grab_food', 'grab_cabs', 'grab_mart'] },
    { id: 'delivery_agent', name: 'Delivery Agent', services: ['grab_food', 'grab_mart'] },
    { id: 'restaurant', name: 'Restaurant', services: ['grab_food'] },
    { id: 'driver', name: 'Driver', services: ['grab_cabs'] },
    { id: 'darkstore', name: 'Dark Store', services: ['grab_mart'] }
  ];

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!userType) {
      setError('Please select a user type');
      return;
    }

    try {
      const response = await api.post('/login', {
        user_type: userType,
        username: credentials.username,
        password: credentials.password
      });

      if (response.data.success) {
        localStorage.setItem('user', JSON.stringify({
          type: userType,
          username: credentials.username,
          services: userTypes.find(type => type.id === userType).services
        }));
        navigate('/dashboard');
      }
    } catch (error) {
      setError('Invalid credentials or server error');
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>GrabHack Customer Service Platform</h1>
        <p>Select your role and login to continue</p>
      </div>

      <div className="card" style={{ maxWidth: '500px', margin: '0 auto' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>Login</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label">Select User Type</label>
            <div className="service-grid">
              {userTypes.map(type => (
                <div
                  key={type.id}
                  className={`service-card ${userType === type.id ? 'selected' : ''}`}
                  onClick={() => setUserType(type.id)}
                >
                  <h3>{type.name}</h3>
                  <p>Services: {type.services.map(s => s.replace('_', ' ')).join(', ')}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
            Login
          </button>
        </form>

        <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <h4>Demo Credentials:</h4>
          <p><strong>Customer:</strong> customer1 / pass123</p>
          <p><strong>Delivery Agent:</strong> agent1 / pass123</p>
          <p><strong>Restaurant:</strong> resto1 / pass123</p>
          <p><strong>Driver:</strong> driver1 / pass123</p>
          <p><strong>Dark Store:</strong> store1 / pass123</p>
        </div>
      </div>
    </div>
  );
};

export default Login;