import React, { useState, useEffect } from 'react';
import api from '../services/api';

const OrderTimeline = ({ orderId, onClose }) => {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!orderId) return;

    const fetchTimeline = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.get(`/order-history/${orderId}`);
        setTimeline(response.data.timeline || []);
      } catch (err) {
        console.error('Error fetching order timeline:', err);
        setError('Failed to load order timeline');
      } finally {
        setLoading(false);
      }
    };

    fetchTimeline();
  }, [orderId]);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    };
  };

  const getActorIcon = (actorType) => {
    const icons = {
      customer: '👤',
      restaurant: '🏪',
      delivery_agent: '🏍️',
      driver: '🚗',
      dark_house: '🏢',
      system: '🤖'
    };
    return icons[actorType] || '📱';
  };

  const getUpdateTypeIcon = (updateType) => {
    const icons = {
      dish_added: '➕',
      dish_removed: '➖',
      route_changed: '🗺️',
      delivery_delayed: '⏰',
      preparation_delayed: '🍳',
      order_ready_early: '✅',
      address_updated: '📍',
      item_substituted: '🔄',
      quality_check_failed: '❌',
      vehicle_upgraded: '🚚',
      fragile_handling_applied: '🔒'
    };
    return icons[updateType] || '🔔';
  };

  const getActorDisplayName = (actorType, actorUsername) => {
    const typeMap = {
      customer: 'Customer',
      restaurant: 'Restaurant',
      delivery_agent: 'Delivery Agent',
      driver: 'Driver',
      dark_house: 'Dark Store',
      system: 'System'
    };

    return `${typeMap[actorType] || actorType} (${actorUsername})`;
  };

  if (loading) {
    return (
      <div className="timeline-modal">
        <div className="timeline-content">
          <div className="timeline-header">
            <h3>Order Timeline</h3>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="timeline-loading">
            <div className="loading-spinner"></div>
            <p>Loading order timeline...</p>
          </div>
        </div>
        <div className="timeline-overlay" onClick={onClose}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="timeline-modal">
        <div className="timeline-content">
          <div className="timeline-header">
            <h3>Order Timeline</h3>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="timeline-error">
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        </div>
        <div className="timeline-overlay" onClick={onClose}></div>
      </div>
    );
  }

  return (
    <div className="timeline-modal">
      <div className="timeline-content">
        <div className="timeline-header">
          <h3>Order Timeline - {orderId}</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="timeline-body">
          {timeline.length === 0 ? (
            <div className="no-timeline">
              <p>No updates yet for this order</p>
            </div>
          ) : (
            <div className="timeline-list">
              {timeline.map((item, index) => {
                const { date, time } = formatTimestamp(item.timestamp);

                return (
                  <div key={index} className="timeline-item">
                    <div className="timeline-marker">
                      <div className="timeline-icon">
                        {getActorIcon(item.actor_type)}
                      </div>
                      <div className="timeline-line"></div>
                    </div>

                    <div className="timeline-content-item">
                      <div className="timeline-update-header">
                        <span className="update-icon">
                          {getUpdateTypeIcon(item.update_type)}
                        </span>
                        <span className="update-type">
                          {item.update_type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className="timeline-timestamp">
                          {date} at {time}
                        </span>
                      </div>

                      <div className="timeline-actor">
                        By {getActorDisplayName(item.actor_type, item.actor_username)}
                      </div>

                      <div className="timeline-description">
                        {item.description}
                      </div>

                      {item.details && Object.keys(item.details).length > 0 && (
                        <div className="timeline-details">
                          <strong>Details:</strong>
                          <ul>
                            {Object.entries(item.details).map(([key, value]) => (
                              <li key={key}>
                                <strong>{key.replace(/_/g, ' ')}:</strong> {value}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="timeline-overlay" onClick={onClose}></div>

      <style jsx>{`
        .timeline-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 2000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .timeline-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: -1;
        }

        .timeline-content {
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
          width: 100%;
          max-width: 600px;
          max-height: 80vh;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .timeline-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #eee;
          background: #f8f9fa;
        }

        .timeline-header h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .close-btn:hover {
          background: rgba(0, 0, 0, 0.1);
        }

        .timeline-body {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
        }

        .timeline-loading, .timeline-error, .no-timeline {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 20px;
          text-align: center;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #007bff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 16px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .timeline-list {
          position: relative;
        }

        .timeline-item {
          display: flex;
          margin-bottom: 24px;
          position: relative;
        }

        .timeline-item:last-child .timeline-line {
          display: none;
        }

        .timeline-marker {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-right: 16px;
          flex-shrink: 0;
        }

        .timeline-icon {
          width: 40px;
          height: 40px;
          background: #007bff;
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          font-weight: bold;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .timeline-line {
          width: 2px;
          background: #e9ecef;
          flex: 1;
          margin-top: 8px;
          min-height: 30px;
        }

        .timeline-content-item {
          flex: 1;
          background: #f8f9fa;
          border-radius: 8px;
          padding: 16px;
          border-left: 4px solid #007bff;
        }

        .timeline-update-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          flex-wrap: wrap;
        }

        .update-icon {
          font-size: 16px;
        }

        .update-type {
          font-weight: 600;
          color: #007bff;
          text-transform: capitalize;
        }

        .timeline-timestamp {
          color: #666;
          font-size: 12px;
          margin-left: auto;
        }

        .timeline-actor {
          color: #666;
          font-size: 13px;
          margin-bottom: 8px;
        }

        .timeline-description {
          color: #333;
          line-height: 1.5;
          margin-bottom: 12px;
        }

        .timeline-details {
          background: white;
          border-radius: 4px;
          padding: 12px;
          border: 1px solid #e9ecef;
        }

        .timeline-details ul {
          margin: 8px 0 0 0;
          padding-left: 20px;
        }

        .timeline-details li {
          margin-bottom: 4px;
          font-size: 13px;
        }

        @media (max-width: 768px) {
          .timeline-modal {
            padding: 10px;
          }

          .timeline-content {
            max-height: 90vh;
          }

          .timeline-header {
            padding: 15px;
          }

          .timeline-body {
            padding: 15px;
          }

          .timeline-update-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
          }

          .timeline-timestamp {
            margin-left: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default OrderTimeline;