import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../Mobile.css';

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

  const getUserTypeDisplay = (type) => {
    const typeMap = {
      'customer': '👤 Customer',
      'delivery_agent': '🏍️ Delivery Agent', 
      'restaurant': '🍳 Restaurant',
      'driver': '🚗 Driver',
      'darkstore': '🏪 Dark Store'
    };
    return typeMap[type] || type;
  };

  const getServiceEmoji = (service) => {
    const serviceMap = {
      'grab_food': '🍕',
      'grab_cabs': '🚗',
      'grab_mart': '🛒'
    };
    return serviceMap[service] || '📱';
  };

  const getStatusClass = (status) => {
    switch(status) {
      case 'completed': return 'completed';
      case 'in_progress': 
      case 'assigned':
      case 'delivering': 
      case 'preparing': return 'in_progress';
      case 'cancelled': return 'cancelled';
      default: return 'in_progress';
    }
  };

  return (
    <div className="App">
      <div className="mobile-container">
        <div className="mobile-header">
          <button className="mobile-header-icon-btn" onClick={handleLogout}>
            ←
          </button>
          <div className="mobile-header-content">
            <h1>Hello, {user.username}!</h1>
            <p>{getUserTypeDisplay(user.type)}</p>
          </div>
        </div>

        <div className="mobile-card">
          <h2>📋 Your Orders & Activities</h2>
          {orders.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#6c757d' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📦</div>
              <p>No orders found</p>
              <p style={{ fontSize: '14px', opacity: 0.8 }}>Your order history will appear here</p>
            </div>
          ) : (
            <div className="mobile-orders-container">
              {orders.map(order => (
                <div key={order.id} className="mobile-order-card">
                  <div className="mobile-order-header">
                    <div className="mobile-order-id">
                      {getServiceEmoji(order.service)} {order.id}
                    </div>
                    <div className={`mobile-order-status ${getStatusClass(order.status)}`}>
                      {order.status.replace('_', ' ')}
                    </div>
                  </div>
                  
                  <div className="mobile-order-details">
                    <div><strong>Service:</strong> {order.service.replace('_', ' ')}</div>
                    <div><strong>Date:</strong> {new Date(order.date).toLocaleDateString()}</div>
                    {order.price && (
                      <div><strong>Price:</strong> ${order.price.toFixed(2)}</div>
                    )}
                    {order.payment_method && (
                      <div><strong>Payment:</strong> {order.payment_method.toUpperCase()}</div>
                    )}
                  </div>

                  {order.restaurant_name && (
                    <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '12px' }}>
                      🍳 {order.restaurant_name}
                    </div>
                  )}
                  
                  <button 
                    className="mobile-btn mobile-btn-secondary mobile-btn-small"
                    onClick={() => handleComplaint(order.service)}
                  >
                    🆘 Report Issue
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mobile-card">
          <h2>🆘 Report Issues</h2>
          <div className="mobile-service-grid">
            {user.services.map(service => (
              <div key={service} className="mobile-service-card" onClick={() => handleComplaint(service)}>
                <h3>{getServiceEmoji(service)} {service.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                <p>Tap to get AI support</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;