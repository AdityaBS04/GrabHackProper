import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../Mobile.css';
import '../EnhancedAnimations.css';
import AnimatedBackground from '../components/AnimatedBackground';
import LoadingSpinner from '../components/LoadingSpinner';
import FloatingActionButton from '../components/FloatingActionButton';
import AnimatedCard from '../components/AnimatedCard';
import InteractiveIcon from '../components/InteractiveIcon';
import PulsingOrb from '../components/PulsingOrb';
import NotificationCenter from '../components/NotificationCenter';
import OrderTimeline from '../components/OrderTimeline';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [selectedService, setSelectedService] = useState('');
  const [selectedOrderId, setSelectedOrderId] = useState(null);
  const [showTimeline, setShowTimeline] = useState(false);
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
      // Try new endpoint first (with update counts)
      let response;
      try {
        response = await api.get(`/orders/${userData.type}/${userData.username}/with-updates`);
      } catch (updateError) {
        // Fallback to original endpoint
        response = await api.get(`/orders/${userData.type}/${userData.username}`);
      }
      setOrders(response.data.orders || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleComplaint = (service, orderId = null) => {
    navigate('/complaint', { state: { service, userType: user.type, orderId } });
  };

  const handleViewTimeline = (orderId) => {
    setSelectedOrderId(orderId);
    setShowTimeline(true);
  };

  const handleCloseTimeline = () => {
    setSelectedOrderId(null);
    setShowTimeline(false);
  };

  if (!user) return (
    <div className="App">
      <AnimatedBackground />
      <LoadingSpinner text="Loading Dashboard..." />
    </div>
  );

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
      'grab_mart': '🛒',
      'grab_express': '📦'
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
      <AnimatedBackground />
      <div className="mobile-container">
        <div className="mobile-header">
          <button className="mobile-header-icon-btn" onClick={handleLogout}>
            ←
          </button>
          <div className="mobile-header-content">
            <h1 className="gradient-text">Hello, {user.username}!</h1>
            <p>{getUserTypeDisplay(user.type)}</p>
          </div>
          <div className="mobile-header-actions">
            <NotificationCenter user={user} />
          </div>
        </div>

        <AnimatedCard>
          <h2>
            <InteractiveIcon icon="📋" size={24} />
            Your Orders & Activities
          </h2>
          {orders.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#6c757d' }}>
              <PulsingOrb size={80} color="#00C851" style={{ margin: '0 auto 16px' }} />
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
                      {(order.update_count > 0 || order.unread_notifications > 0) && (
                        <span className="order-update-badge">
                          {order.unread_notifications > 0
                            ? `${order.unread_notifications} new`
                            : `${order.update_count} updates`}
                        </span>
                      )}
                    </div>
                    <div className={`mobile-order-status ${getStatusClass(order.status)}`}>
                      {order.status.replace('_', ' ')}
                    </div>
                  </div>

                  {/* Show current status remarks if available */}
                  {order.current_status_remarks && order.current_status_remarks !== 'Order placed' && (
                    <div className="order-status-remarks">
                      💬 {order.current_status_remarks}
                      {order.last_updated_by && (
                        <span className="last-updated-by">
                          - Updated by {order.last_updated_by}
                        </span>
                      )}
                    </div>
                  )}
                  
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
                  
                  {/* Display food items for grab_food orders */}
                  {order.service === 'grab_food' && order.food_items && (
                    <div style={{ fontSize: '14px', color: '#495057', marginBottom: '12px', padding: '8px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                      <strong>🍽️ Items ordered:</strong>
                      <div style={{ marginTop: '4px', fontStyle: 'italic' }}>
                        {order.food_items}
                      </div>
                    </div>
                  )}
                  
                  {/* Display products for grab_mart orders */}
                  {order.service === 'grab_mart' && order.products_ordered && (
                    <div style={{ fontSize: '14px', color: '#495057', marginBottom: '12px', padding: '8px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                      <strong>🛒 Products ordered:</strong>
                      <div style={{ marginTop: '4px', fontStyle: 'italic' }}>
                        {order.products_ordered}
                      </div>
                    </div>
                  )}
                  
                  {/* Display packages for grab_express orders */}
                  {order.service === 'grab_express' && order.products_ordered && (
                    <div style={{ fontSize: '14px', color: '#495057', marginBottom: '12px', padding: '8px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                      <strong>📦 Package details:</strong>
                      <div style={{ marginTop: '4px', fontStyle: 'italic' }}>
                        {order.products_ordered}
                      </div>
                      {order.details && order.details.vehicle_type && (
                        <div style={{ marginTop: '4px', fontSize: '12px', color: '#6c757d' }}>
                          🚚 Vehicle: {order.details.vehicle_type}
                        </div>
                      )}
                    </div>
                  )}

                  <div className="order-actions">
                    <button
                      className="mobile-btn mobile-btn-primary mobile-btn-small"
                      onClick={() => handleViewTimeline(order.id)}
                      title="View order timeline and updates"
                    >
                      📋 Timeline
                      {order.update_count > 0 && (
                        <span className="btn-badge">{order.update_count}</span>
                      )}
                    </button>
                    <button
                      className="mobile-btn mobile-btn-secondary mobile-btn-small"
                      onClick={() => handleComplaint(order.service, order.id)}
                    >
                      🆘 Report Issue
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </AnimatedCard>

        <AnimatedCard>
          <h2>
            <InteractiveIcon icon="🆘" size={24} hoverColor="#dc3545" />
            Report Issues
          </h2>
          <div className="mobile-service-grid">
            {user.services.map(service => (
              <div key={service} className="mobile-service-card" onClick={() => handleComplaint(service)}>
                <h3>{getServiceEmoji(service)} {service.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                <p>Tap to get AI support</p>
              </div>
            ))}
          </div>
        </AnimatedCard>
        
        <FloatingActionButton
          onClick={() => navigate('/complaint')}
          icon="🆘"
        />

        {/* Order Timeline Modal */}
        {showTimeline && selectedOrderId && (
          <OrderTimeline
            orderId={selectedOrderId}
            onClose={handleCloseTimeline}
          />
        )}
      </div>

      <style jsx>{`
        .order-update-badge {
          background: #ff4444;
          color: white;
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
          margin-left: 8px;
          font-weight: bold;
        }

        .order-status-remarks {
          background: #e3f2fd;
          border-left: 4px solid #2196f3;
          padding: 8px 12px;
          margin: 8px 0;
          font-size: 13px;
          border-radius: 4px;
        }

        .last-updated-by {
          color: #666;
          font-size: 11px;
          font-style: italic;
        }

        .order-actions {
          display: flex;
          gap: 8px;
          margin-top: 12px;
          flex-wrap: wrap;
        }

        .btn-badge {
          background: #fff;
          color: #007bff;
          font-size: 10px;
          padding: 1px 4px;
          border-radius: 8px;
          margin-left: 4px;
          font-weight: bold;
        }

        .mobile-btn-primary {
          background: #007bff;
          color: white;
          position: relative;
        }

        .mobile-btn-primary:hover {
          background: #0056b3;
        }

        @media (max-width: 480px) {
          .order-actions {
            flex-direction: column;
          }

          .mobile-btn-small {
            font-size: 12px;
            padding: 8px 12px;
          }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;