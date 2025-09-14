"""
Cross-Actor Update Service
Handles automatic notifications and updates between different actors in the Grab ecosystem
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CrossActorUpdateService:
    """Service to handle cross-actor updates and notifications"""

    def __init__(self, database_path: str = 'grabhack.db'):
        self.database_path = database_path

        # Define update type mappings and affected actors
        self.update_mappings = {
            # Restaurant updates
            'dish_added': {
                'description_template': 'Restaurant added {item} due to {reason}',
                'affected_actors': ['customer'],
                'notification_template': 'Good news! {restaurant_name} added complimentary {item} to your order due to {reason}'
            },
            'dish_removed': {
                'description_template': 'Restaurant removed {item} - {reason}',
                'affected_actors': ['customer'],
                'notification_template': '{restaurant_name} had to remove {item} from your order: {reason}. Refund will be processed.'
            },
            'preparation_delayed': {
                'description_template': 'Restaurant needs extra {minutes} minutes due to {reason}',
                'affected_actors': ['customer', 'delivery_agent'],
                'notification_template': 'Your order will be ready in {minutes} extra minutes due to {reason}'
            },
            'order_ready_early': {
                'description_template': 'Restaurant completed order {minutes} minutes early',
                'affected_actors': ['customer', 'delivery_agent'],
                'notification_template': 'Great news! Your order is ready {minutes} minutes early and awaiting pickup'
            },

            # Driver/Delivery agent updates
            'route_changed': {
                'description_template': 'Driver taking {new_route} due to {reason}',
                'affected_actors': ['customer', 'restaurant'],
                'notification_template': 'Driver is taking an alternate route ({route_description}) due to {reason}. ETA updated to {new_eta}'
            },
            'delivery_delayed': {
                'description_template': 'Delivery delayed by {minutes} minutes due to {reason}',
                'affected_actors': ['customer', 'restaurant'],
                'notification_template': 'Your delivery is delayed by {minutes} minutes due to {reason}. New ETA: {new_eta}'
            },
            'address_clarification_needed': {
                'description_template': 'Driver needs address clarification: {issue}',
                'affected_actors': ['customer'],
                'notification_template': 'Your delivery partner needs clarification about your address: {issue}. Please check your phone.'
            },
            'driver_arrived': {
                'description_template': 'Driver arrived at {location}',
                'affected_actors': ['customer', 'restaurant'],
                'notification_template': 'Your delivery partner has arrived at {location}'
            },

            # Customer updates
            'address_updated': {
                'description_template': 'Customer updated delivery address to {new_address}',
                'affected_actors': ['delivery_agent', 'restaurant'],
                'notification_template': 'Customer updated delivery address to: {new_address}'
            },
            'order_modified': {
                'description_template': 'Customer modified order: {changes}',
                'affected_actors': ['restaurant', 'delivery_agent'],
                'notification_template': 'Customer updated their order: {changes}'
            },
            'special_instructions_added': {
                'description_template': 'Customer added delivery instructions: {instructions}',
                'affected_actors': ['delivery_agent'],
                'notification_template': 'Customer added special instructions: {instructions}'
            },

            # Grab Express specific
            'vehicle_upgraded': {
                'description_template': 'Package delivery upgraded from {old_vehicle} to {new_vehicle} due to {reason}',
                'affected_actors': ['customer'],
                'notification_template': 'Your package delivery has been upgraded from {old_vehicle} to {new_vehicle} for {reason}'
            },
            'fragile_handling_applied': {
                'description_template': 'Special fragile item handling applied due to package contents',
                'affected_actors': ['customer'],
                'notification_template': 'We\'ve applied special fragile item handling to ensure your package arrives safely'
            },

            # Dark store updates
            'item_substituted': {
                'description_template': 'Dark store substituted {original_item} with {substitute_item} due to stock shortage',
                'affected_actors': ['customer', 'delivery_agent'],
                'notification_template': 'We substituted {original_item} with {substitute_item} (same/better quality) due to availability'
            },
            'quality_check_failed': {
                'description_template': 'Dark store removed {item} due to quality concerns',
                'affected_actors': ['customer'],
                'notification_template': 'We removed {item} from your order due to quality standards. Refund processed.'
            }
        }

        # Spam prevention settings
        self.spam_limits = {
            'max_updates_per_order_per_hour': 5,
            'max_updates_per_actor_per_hour': 10,
            'duplicate_update_window_minutes': 10
        }

    def create_cross_actor_update(self, order_id: str, actor_type: str, actor_username: str,
                                update_type: str, details: Dict[str, Any]) -> bool:
        """
        Create a cross-actor update and generate notifications for affected actors

        Args:
            order_id: The order being updated
            actor_type: Type of actor making the update (restaurant, driver, customer, etc.)
            actor_username: Username of actor making the update
            update_type: Type of update (dish_added, route_changed, etc.)
            details: Dictionary with update-specific information

        Returns:
            bool: True if update was created successfully, False if blocked by spam prevention
        """
        try:
            # Check spam prevention first
            if not self._check_spam_limits(order_id, actor_type, actor_username, update_type):
                logger.warning(f"Update blocked by spam prevention: {order_id}, {actor_type}, {update_type}")
                return False

            # Get update mapping
            if update_type not in self.update_mappings:
                logger.error(f"Unknown update type: {update_type}")
                return False

            update_config = self.update_mappings[update_type]

            # Generate description
            description = self._generate_description(update_config['description_template'], details)

            # Create the update record
            update_id = self._create_update_record(
                order_id, actor_type, actor_username, update_type,
                description, details, update_config['affected_actors']
            )

            if not update_id:
                return False

            # Update the order's status and remarks
            self._update_order_status(order_id, actor_username, description)

            # Generate notifications for affected actors
            self._generate_notifications(order_id, update_id, update_config, details)

            logger.info(f"Cross-actor update created successfully: {update_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating cross-actor update: {e}")
            return False

    def _check_spam_limits(self, order_id: str, actor_type: str, actor_username: str, update_type: str) -> bool:
        """Check if update violates spam prevention rules"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            # Check updates per order per hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            cursor.execute('''
                SELECT COUNT(*) FROM order_updates
                WHERE order_id = ? AND timestamp > ?
            ''', (order_id, one_hour_ago.isoformat()))

            order_updates_count = cursor.fetchone()[0]
            if order_updates_count >= self.spam_limits['max_updates_per_order_per_hour']:
                return False

            # Check updates per actor per hour
            cursor.execute('''
                SELECT COUNT(*) FROM order_updates
                WHERE actor_username = ? AND timestamp > ?
            ''', (actor_username, one_hour_ago.isoformat()))

            actor_updates_count = cursor.fetchone()[0]
            if actor_updates_count >= self.spam_limits['max_updates_per_actor_per_hour']:
                return False

            # Check for duplicate updates within window
            duplicate_window = datetime.now() - timedelta(minutes=self.spam_limits['duplicate_update_window_minutes'])
            cursor.execute('''
                SELECT COUNT(*) FROM order_updates
                WHERE order_id = ? AND actor_username = ? AND update_type = ? AND timestamp > ?
            ''', (order_id, actor_username, update_type, duplicate_window.isoformat()))

            duplicate_count = cursor.fetchone()[0]
            if duplicate_count > 0:
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking spam limits: {e}")
            return False
        finally:
            conn.close()

    def _create_update_record(self, order_id: str, actor_type: str, actor_username: str,
                             update_type: str, description: str, details: Dict[str, Any],
                             affected_actors: List[str]) -> Optional[int]:
        """Create the update record in database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO order_updates
                (order_id, actor_type, actor_username, update_type, description, details, affected_actors)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, actor_type, actor_username, update_type, description,
                  json.dumps(details), json.dumps(affected_actors)))

            update_id = cursor.lastrowid
            conn.commit()
            return update_id

        except Exception as e:
            logger.error(f"Error creating update record: {e}")
            return None
        finally:
            conn.close()

    def _update_order_status(self, order_id: str, updated_by: str, remarks: str):
        """Update the order's status tracking"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE orders
                SET last_updated_by = ?, last_update_timestamp = ?,
                    update_count = update_count + 1, current_status_remarks = ?
                WHERE id = ?
            ''', (updated_by, datetime.now().isoformat(), remarks, order_id))

            conn.commit()

        except Exception as e:
            logger.error(f"Error updating order status: {e}")
        finally:
            conn.close()

    def _generate_notifications(self, order_id: str, update_id: int, update_config: Dict, details: Dict[str, Any]):
        """Generate notifications for affected actors"""
        # Get order details to identify target actors
        order_info = self._get_order_info(order_id)
        if not order_info:
            return

        target_actors = self._identify_target_actors(order_info, update_config['affected_actors'])

        # Generate notification message
        notification_message = self._generate_notification_message(update_config['notification_template'], details, order_info)

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            for actor_type, username in target_actors:
                cursor.execute('''
                    INSERT INTO actor_notifications
                    (order_id, target_actor_type, target_username, notification_type, message, source_update_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (order_id, actor_type, username, 'order_update', notification_message, update_id))

            conn.commit()
            logger.info(f"Generated {len(target_actors)} notifications for update {update_id}")

        except Exception as e:
            logger.error(f"Error generating notifications: {e}")
        finally:
            conn.close()

    def _get_order_info(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order information for notification generation"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT service, customer_id, restaurant_id, driver_id, restaurant_name,
                       username, user_type, start_address, end_address, details
                FROM orders WHERE id = ?
            ''', (order_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'service': row[0],
                'customer_id': row[1],
                'restaurant_id': row[2],
                'driver_id': row[3],
                'restaurant_name': row[4],
                'username': row[5],
                'user_type': row[6],
                'start_address': row[7],
                'end_address': row[8],
                'details': json.loads(row[9]) if row[9] else {}
            }

        except Exception as e:
            logger.error(f"Error getting order info: {e}")
            return None
        finally:
            conn.close()

    def _identify_target_actors(self, order_info: Dict[str, Any], affected_actor_types: List[str]) -> List[tuple]:
        """Identify specific usernames for each affected actor type"""
        targets = []

        for actor_type in affected_actor_types:
            if actor_type == 'customer' and order_info.get('username'):
                # Find customer username from the order
                if order_info.get('user_type') == 'customer':
                    targets.append(('customer', order_info['username']))
                else:
                    # Need to find the customer username for this order
                    customer_username = self._find_customer_for_order(order_info)
                    if customer_username:
                        targets.append(('customer', customer_username))

            elif actor_type == 'restaurant' and order_info.get('restaurant_id'):
                targets.append(('restaurant', order_info['restaurant_id']))

            elif actor_type == 'delivery_agent' and order_info.get('driver_id'):
                targets.append(('delivery_agent', order_info['driver_id']))

            elif actor_type == 'driver' and order_info.get('driver_id'):
                targets.append(('driver', order_info['driver_id']))

        return targets

    def _find_customer_for_order(self, order_info: Dict[str, Any]) -> Optional[str]:
        """Find customer username for orders created by other actors"""
        # For grab_food orders, customer_id usually contains the customer info
        if order_info.get('customer_id'):
            return order_info['customer_id'].replace('CUST', 'customer')

        # Could also query orders table to find matching customer order
        return None

    def _generate_description(self, template: str, details: Dict[str, Any]) -> str:
        """Generate human-readable description from template"""
        try:
            return template.format(**details)
        except KeyError as e:
            logger.warning(f"Missing key in details for template: {e}")
            return template
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return "Update details unavailable"

    def _generate_notification_message(self, template: str, details: Dict[str, Any], order_info: Dict[str, Any]) -> str:
        """Generate notification message with order context"""
        try:
            # Merge details with order info for template
            template_data = {**details, **order_info}
            return template.format(**template_data)
        except Exception as e:
            logger.error(f"Error generating notification message: {e}")
            return "Order has been updated. Please check your order details."

    def get_notifications_for_actor(self, actor_type: str, username: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a specific actor"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            query = '''
                SELECT id, order_id, notification_type, message, is_read, created_at
                FROM actor_notifications
                WHERE target_actor_type = ? AND target_username = ?
            '''
            params = [actor_type, username]

            if unread_only:
                query += ' AND is_read = 0'

            query += ' ORDER BY created_at DESC LIMIT 50'

            cursor.execute(query, params)
            rows = cursor.fetchall()

            notifications = []
            for row in rows:
                notifications.append({
                    'id': row[0],
                    'order_id': row[1],
                    'type': row[2],
                    'message': row[3],
                    'is_read': bool(row[4]),
                    'created_at': row[5]
                })

            return notifications

        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
        finally:
            conn.close()

    def mark_notification_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE actor_notifications
                SET is_read = 1
                WHERE id = ?
            ''', (notification_id,))

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
        finally:
            conn.close()

    def get_order_update_timeline(self, order_id: str) -> List[Dict[str, Any]]:
        """Get complete update timeline for an order"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT actor_type, actor_username, update_type, description, timestamp, details
                FROM order_updates
                WHERE order_id = ?
                ORDER BY timestamp ASC
            ''', (order_id,))

            rows = cursor.fetchall()
            timeline = []

            for row in rows:
                timeline.append({
                    'actor_type': row[0],
                    'actor_username': row[1],
                    'update_type': row[2],
                    'description': row[3],
                    'timestamp': row[4],
                    'details': json.loads(row[5]) if row[5] else {}
                })

            return timeline

        except Exception as e:
            logger.error(f"Error getting order timeline: {e}")
            return []
        finally:
            conn.close()