#!/usr/bin/env python3
"""
Test script for missing items functionality
Creates test orders and tests the missing items handler
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the GrabHack directory to sys.path
sys.path.append(os.path.dirname(__file__))

def create_test_order():
    """Create a test order for missing items testing"""
    db_path = 'grabhack.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create a test order with food items
        test_order_data = {
            'id': 'TEST12345',
            'username': 'test_user',
            'service': 'grab_food',
            'user_type': 'customer',
            'restaurant_name': 'Pizza Palace',
            'food_items': 'Chicken Biryani, Garlic Naan, Mango Lassi, Raita',
            'price': 25.99,
            'status': 'completed',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Insert test order
        cursor.execute('''
            INSERT OR REPLACE INTO orders (id, username, service, user_type, restaurant_name, food_items, price, status, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_order_data['id'],
            test_order_data['username'],
            test_order_data['service'],
            test_order_data['user_type'],
            test_order_data['restaurant_name'],
            test_order_data['food_items'],
            test_order_data['price'],
            test_order_data['status'],
            test_order_data['date']
        ))

        # Create test user if not exists
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, password, user_type, credibility_score)
            VALUES (?, ?, ?, ?)
        ''', ('test_user', 'test123', 'customer', 7))

        conn.commit()
        conn.close()

        print(f"Test order created: {test_order_data['id']}")
        print(f"Items: {test_order_data['food_items']}")
        print(f"Restaurant: {test_order_data['restaurant_name']}")
        print(f"Price: ${test_order_data['price']}")
        return test_order_data['id']

    except Exception as e:
        print(f"Error creating test order: {e}")
        return None

def test_missing_items_handler():
    """Test the missing items handler directly"""
    try:
        from grab_food.customer.order_quality_handler import OrderQualityHandler

        handler = OrderQualityHandler()

        print("\nTesting missing items handler...")

        # Test with no order_id (should get most recent)
        response1 = handler.handle_missing_items(
            query="I want to report missing items",
            image_data=None,
            username="test_user",
            order_id=None
        )

        print(f"Response 1 (no order_id): {response1[:200]}...")

        # Test with specific order_id
        response2 = handler.handle_missing_items(
            query="Missing items complaint",
            image_data=None,
            username="test_user",
            order_id="TEST12345"
        )

        print(f"Response 2 (with order_id): {response2[:200]}...")

        return True

    except Exception as e:
        print(f"Error testing handler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Missing Items Test")

    # Create test order
    order_id = create_test_order()
    if not order_id:
        print("Failed to create test order")
        sys.exit(1)

    # Test handler
    success = test_missing_items_handler()
    if success:
        print("Missing items handler test completed")
    else:
        print("Missing items handler test failed")
        sys.exit(1)

    print(f"\nNow you can test in the frontend:")
    print(f"1. Login as 'test_user'")
    print(f"2. Go to order {order_id}")
    print(f"3. Click 'Report Issue'")
    print(f"4. Select 'Missing items in delivery'")
    print(f"5. You should see the interactive selection interface!")