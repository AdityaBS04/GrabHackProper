import React, { useState, useEffect } from 'react';
import notificationService from '../services/notificationService';

const NotificationCenter = ({ user }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;

    // Start polling for notifications
    notificationService.startPolling(user.user_type || user.type, user.username);

    // Add listener for notification updates
    const handleNotificationUpdate = ({ notifications, unreadCount }) => {
      setNotifications(notifications);
      setUnreadCount(unreadCount);
    };

    notificationService.addListener(handleNotificationUpdate);

    // Cleanup on unmount
    return () => {
      notificationService.removeListener(handleNotificationUpdate);
      notificationService.stopPolling();
    };
  }, [user]);

  const handleMarkAsRead = async (notificationId) => {
    setLoading(true);
    try {
      await notificationService.markAsRead(notificationId);
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
    setLoading(false);
  };

  const handleMarkAllAsRead = async () => {
    setLoading(true);
    try {
      await notificationService.markAllAsRead();
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
    setLoading(false);
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const notificationTime = new Date(timestamp);
    const diffMs = now - notificationTime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const getNotificationIcon = (type) => {
    const icons = {
      order_update: '📦',
      route_changed: '🗺️',
      dish_added: '🍽️',
      delivery_delayed: '⏰',
      default: '🔔'
    };
    return icons[type] || icons.default;
  };

  return (
    <div className="notification-center">
      {/* Notification Bell */}
      <button
        className={`notification-bell ${unreadCount > 0 ? 'has-notifications' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Notifications"
      >
        🔔
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h4>Notifications</h4>
            {unreadCount > 0 && (
              <button
                className="mark-all-read-btn"
                onClick={handleMarkAllAsRead}
                disabled={loading}
              >
                Mark all as read
              </button>
            )}
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <div className="no-notifications">
                <p>No notifications yet</p>
              </div>
            ) : (
              notifications.slice(0, 10).map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                  onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
                >
                  <div className="notification-icon">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="notification-content">
                    <div className="notification-message">
                      {notification.message}
                    </div>
                    <div className="notification-meta">
                      <span className="notification-time">
                        {formatTimeAgo(notification.created_at)}
                      </span>
                      {notification.order_id && (
                        <span className="notification-order">
                          Order: {notification.order_id}
                        </span>
                      )}
                    </div>
                  </div>
                  {!notification.is_read && (
                    <div className="unread-indicator"></div>
                  )}
                </div>
              ))
            )}
          </div>

          {notifications.length > 10 && (
            <div className="notification-footer">
              <button className="view-all-btn">
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div
          className="notification-overlay"
          onClick={() => setIsOpen(false)}
        ></div>
      )}

      <style jsx>{`
        .notification-center {
          position: relative;
          display: inline-block;
        }

        .notification-bell {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          position: relative;
          padding: 8px;
          border-radius: 50%;
          transition: background-color 0.2s;
        }

        .notification-bell:hover {
          background-color: rgba(0, 0, 0, 0.05);
        }

        .notification-bell.has-notifications {
          animation: bellRing 2s ease-in-out infinite;
        }

        @keyframes bellRing {
          0%, 100% { transform: rotate(0deg); }
          10% { transform: rotate(10deg); }
          20% { transform: rotate(-10deg); }
          30% { transform: rotate(5deg); }
          40% { transform: rotate(-5deg); }
          50% { transform: rotate(0deg); }
        }

        .notification-badge {
          position: absolute;
          top: 0;
          right: 0;
          background: #ff4444;
          color: white;
          border-radius: 50%;
          padding: 2px 6px;
          font-size: 12px;
          font-weight: bold;
          min-width: 18px;
          height: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .notification-dropdown {
          position: absolute;
          top: 100%;
          right: 0;
          background: white;
          border: 1px solid #ddd;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          width: 350px;
          max-height: 400px;
          z-index: 1000;
          overflow: hidden;
        }

        .notification-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border-bottom: 1px solid #eee;
          background: #f8f9fa;
        }

        .notification-header h4 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        .mark-all-read-btn {
          background: none;
          border: none;
          color: #007bff;
          cursor: pointer;
          font-size: 12px;
          text-decoration: underline;
        }

        .mark-all-read-btn:hover {
          color: #0056b3;
        }

        .notification-list {
          max-height: 300px;
          overflow-y: auto;
        }

        .no-notifications {
          padding: 40px 20px;
          text-align: center;
          color: #666;
        }

        .notification-item {
          display: flex;
          align-items: flex-start;
          padding: 12px 16px;
          border-bottom: 1px solid #f0f0f0;
          cursor: pointer;
          transition: background-color 0.2s;
          position: relative;
        }

        .notification-item:hover {
          background-color: #f8f9fa;
        }

        .notification-item.unread {
          background-color: #f0f8ff;
        }

        .notification-icon {
          font-size: 20px;
          margin-right: 12px;
          flex-shrink: 0;
        }

        .notification-content {
          flex: 1;
        }

        .notification-message {
          font-size: 14px;
          line-height: 1.4;
          margin-bottom: 4px;
        }

        .notification-meta {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #666;
        }

        .notification-time {
          font-weight: 500;
        }

        .notification-order {
          color: #007bff;
        }

        .unread-indicator {
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          width: 8px;
          height: 8px;
          background: #007bff;
          border-radius: 50%;
        }

        .notification-footer {
          padding: 12px 16px;
          text-align: center;
          border-top: 1px solid #eee;
          background: #f8f9fa;
        }

        .view-all-btn {
          background: none;
          border: none;
          color: #007bff;
          cursor: pointer;
          font-weight: 500;
          text-decoration: underline;
        }

        .view-all-btn:hover {
          color: #0056b3;
        }

        .notification-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 999;
        }
      `}</style>
    </div>
  );
};

export default NotificationCenter;