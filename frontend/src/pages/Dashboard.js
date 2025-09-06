import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [selectedService, setSelectedService] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }
    
    const parsedUser = JSON.parse(userData);
    setUser(parsedUser);
    fetchOrders(parsedUser);
  }, [navigate]);

  const fetchOrders = async (userData) => {
    try {
      const response = await api.get(`/orders/${userData.type}/${userData.username}`);
      setOrders(response.data.orders || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleComplaint = (service) => {
    navigate('/complaint', { state: { service, userType: user.type } });
  };

  if (!user) return <div>Loading...</div>;

  return (
    <div className="container">
      <div className="header">
        <h1>Welcome, {user.username}</h1>
        <p>User Type: {user.type.replace('_', ' ').toUpperCase()}</p>
        <button className="btn btn-secondary" onClick={handleLogout} style={{ float: 'right' }}>
          Logout
        </button>
      </div>

      <div className="card">
        <h2>Available Services</h2>
        <div className="service-grid">
          {user.services.map(service => (
            <div key={service} className="service-card" onClick={() => handleComplaint(service)}>
              <h3>{service.replace('_', ' ').toUpperCase()}</h3>
              <p>Click to submit a complaint</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>Your Orders/Activities</h2>
        {orders.length === 0 ? (
          <p>No orders found</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #dee2e6' }}>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Order ID</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Service</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Date</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '10px' }}>{order.id}</td>
                    <td style={{ padding: '10px' }}>{order.service}</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        backgroundColor: order.status === 'completed' ? '#d4edda' : '#fff3cd',
                        color: order.status === 'completed' ? '#155724' : '#856404'
                      }}>
                        {order.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px' }}>{new Date(order.date).toLocaleDateString()}</td>
                    <td style={{ padding: '10px' }}>
                      <button 
                        className="btn btn-secondary" 
                        onClick={() => handleComplaint(order.service)}
                        style={{ padding: '6px 12px', fontSize: '14px' }}
                      >
                        Report Issue
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;