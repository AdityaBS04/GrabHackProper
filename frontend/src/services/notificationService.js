import api from './api';

class NotificationService {
  constructor() {
    this.listeners = [];
    this.notificationCache = new Map();
    this.pollingInterval = null;
    this.isPolling = false;
  }

  // Start polling for notifications for a specific user
  startPolling(userType, username, intervalMs = 10000) {
    if (this.isPolling) {
      this.stopPolling();
    }

    this.isPolling = true;
    this.userType = userType;
    this.username = username;

    // Initial fetch
    this.fetchNotifications();

    // Set up polling
    this.pollingInterval = setInterval(() => {
      if (this.isPolling) {
        this.fetchNotifications();
      }
    }, intervalMs);
  }

  // Stop polling
  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    this.isPolling = false;
  }

  // Fetch notifications from API
  async fetchNotifications() {
    if (!this.userType || !this.username) return;

    try {
      const response = await api.get(`/notifications/${this.userType}/${this.username}`);
      const notifications = response.data.notifications || [];

      // Check for new notifications
      const newNotifications = this.getNewNotifications(notifications);

      if (newNotifications.length > 0) {
        // Show toast notifications for new items
        newNotifications.forEach(notification => {
          this.showToastNotification(notification);
        });

        // Update cache
        this.updateNotificationCache(notifications);

        // Notify listeners
        this.notifyListeners(notifications, newNotifications);
      }

    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  }

  // Get new notifications by comparing with cache
  getNewNotifications(currentNotifications) {
    const cacheKey = `${this.userType}_${this.username}`;
    const cached = this.notificationCache.get(cacheKey) || [];

    return currentNotifications.filter(current =>
      !cached.some(cached => cached.id === current.id)
    );
  }

  // Update notification cache
  updateNotificationCache(notifications) {
    const cacheKey = `${this.userType}_${this.username}`;
    this.notificationCache.set(cacheKey, notifications);
  }

  // Show browser toast notification
  showToastNotification(notification) {
    // Request notification permission if not granted
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }

    if (Notification.permission === 'granted') {
      const title = this.getNotificationTitle(notification.type);
      const options = {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: `grab-notification-${notification.id}`,
        data: notification
      };

      const browserNotification = new Notification(title, options);

      browserNotification.onclick = () => {
        // Focus the window when notification is clicked
        window.focus();
        browserNotification.close();

        // Mark as read
        this.markAsRead(notification.id);
      };

      // Auto close after 5 seconds
      setTimeout(() => {
        browserNotification.close();
      }, 5000);
    } else {
      // Fallback to in-app toast
      this.showInAppToast(notification);
    }
  }

  // Show in-app toast notification
  showInAppToast(notification) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'notification-toast';
    toast.innerHTML = `
      <div class="toast-header">
        <strong>${this.getNotificationTitle(notification.type)}</strong>
        <button type="button" class="close-toast" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
      <div class="toast-body">
        ${notification.message}
      </div>
    `;

    // Add styles
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      padding: 15px;
      max-width: 300px;
      z-index: 1000;
      animation: slideInRight 0.3s ease-out;
    `;

    // Add to document
    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 5000);

    // Mark as read when clicked
    toast.onclick = () => {
      this.markAsRead(notification.id);
      toast.remove();
    };
  }

  // Get notification title based on type
  getNotificationTitle(type) {
    const titles = {
      order_update: 'Order Update',
      route_changed: 'Route Changed',
      dish_added: 'Item Added',
      delivery_delayed: 'Delivery Update',
      default: 'Grab Notification'
    };
    return titles[type] || titles.default;
  }

  // Mark notification as read
  async markAsRead(notificationId) {
    try {
      await api.put(`/notifications/${notificationId}/read`);

      // Update cache to mark as read
      const cacheKey = `${this.userType}_${this.username}`;
      const cached = this.notificationCache.get(cacheKey) || [];
      const updated = cached.map(n =>
        n.id === notificationId ? { ...n, is_read: true } : n
      );
      this.notificationCache.set(cacheKey, updated);

      // Notify listeners of the change
      this.notifyListeners(updated, []);

    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  }

  // Add event listener
  addListener(callback) {
    this.listeners.push(callback);
  }

  // Remove event listener
  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  // Notify all listeners
  notifyListeners(notifications, newNotifications) {
    this.listeners.forEach(callback => {
      callback({
        notifications,
        newNotifications,
        unreadCount: notifications.filter(n => !n.is_read).length
      });
    });
  }

  // Get cached notifications
  getCachedNotifications() {
    if (!this.userType || !this.username) return [];
    const cacheKey = `${this.userType}_${this.username}`;
    return this.notificationCache.get(cacheKey) || [];
  }

  // Get unread count
  getUnreadCount() {
    return this.getCachedNotifications().filter(n => !n.is_read).length;
  }

  // Mark all notifications as read
  async markAllAsRead() {
    const notifications = this.getCachedNotifications();
    const unreadNotifications = notifications.filter(n => !n.is_read);

    try {
      // Mark all unread notifications as read
      await Promise.all(
        unreadNotifications.map(n =>
          api.put(`/notifications/${n.id}/read`)
        )
      );

      // Update cache
      const cacheKey = `${this.userType}_${this.username}`;
      const updated = notifications.map(n => ({ ...n, is_read: true }));
      this.notificationCache.set(cacheKey, updated);

      // Notify listeners
      this.notifyListeners(updated, []);

    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  }
}

// Create singleton instance
const notificationService = new NotificationService();

export default notificationService;