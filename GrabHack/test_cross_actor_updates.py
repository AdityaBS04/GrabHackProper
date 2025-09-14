#!/usr/bin/env python3
"""
Test script to demonstrate cross-actor updates and notifications
"""

import sys
import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8000/api"

def test_cross_actor_updates():
    """Test the cross-actor update system"""
    print("🧪 Testing Cross-Actor Update System\n")

    # Test 1: Restaurant adds dish due to inconvenience
    print("1. 🍽️ Testing Restaurant Dish Addition...")
    dish_addition_data = {
        "order_id": "GF001",
        "actor_type": "restaurant",
        "actor_username": "resto1",
        "update_type": "dish_added",
        "details": {
            "item": "complimentary garlic bread",
            "reason": "pizza size smaller than expected",
            "restaurant_name": "Pizza Palace"
        }
    }

    response = requests.post(f"{API_BASE}/order-update", json=dish_addition_data)
    if response.status_code == 200:
        print("   ✅ Dish addition update created successfully")
    else:
        print(f"   ❌ Failed to create dish addition update: {response.text}")

    time.sleep(1)

    # Test 2: Driver reports route change
    print("\n2. 🚗 Testing Driver Route Change...")
    route_change_data = {
        "order_id": "GF001",
        "actor_type": "driver",
        "actor_username": "agent1",
        "update_type": "route_changed",
        "details": {
            "new_route": "Highway 101",
            "route_description": "Highway 101 instead of Main Street",
            "reason": "Main Street closure due to construction",
            "new_eta": "20:10 PM (10 minutes delay)"
        }
    }

    response = requests.post(f"{API_BASE}/order-update", json=route_change_data)
    if response.status_code == 200:
        print("   ✅ Route change update created successfully")
    else:
        print(f"   ❌ Failed to create route change update: {response.text}")

    time.sleep(1)

    # Test 3: Customer address update
    print("\n3. 👤 Testing Customer Address Update...")
    address_update_data = {
        "order_id": "GF001",
        "actor_type": "customer",
        "actor_username": "customer1",
        "update_type": "address_updated",
        "details": {
            "new_address": "123 Oak Street Apartment 4B, Jayanagar (Updated with door code: #4321)",
        }
    }

    response = requests.post(f"{API_BASE}/order-update", json=address_update_data)
    if response.status_code == 200:
        print("   ✅ Address update created successfully")
    else:
        print(f"   ❌ Failed to create address update: {response.text}")

    time.sleep(1)

    # Test 4: Check notifications for customer
    print("\n4. 🔔 Checking Customer Notifications...")
    response = requests.get(f"{API_BASE}/notifications/customer/customer1")
    if response.status_code == 200:
        notifications = response.json().get('notifications', [])
        print(f"   📱 Customer has {len(notifications)} notifications:")
        for notification in notifications[:3]:  # Show first 3
            print(f"      - {notification['message']}")
            print(f"        (Created: {notification['created_at']}, Read: {notification['is_read']})")
    else:
        print(f"   ❌ Failed to get customer notifications: {response.text}")

    # Test 5: Check notifications for restaurant
    print("\n5. 🏪 Checking Restaurant Notifications...")
    response = requests.get(f"{API_BASE}/notifications/restaurant/REST001")
    if response.status_code == 200:
        notifications = response.json().get('notifications', [])
        print(f"   📱 Restaurant has {len(notifications)} notifications:")
        for notification in notifications[:3]:  # Show first 3
            print(f"      - {notification['message']}")
    else:
        print(f"   ❌ Failed to get restaurant notifications: {response.text}")

    # Test 6: Check order timeline
    print("\n6. 📋 Checking Order Timeline...")
    response = requests.get(f"{API_BASE}/order-history/GF001")
    if response.status_code == 200:
        timeline = response.json().get('timeline', [])
        print(f"   📊 Order GF001 has {len(timeline)} timeline entries:")
        for entry in timeline:
            print(f"      - {entry['timestamp']}: {entry['description']}")
            print(f"        By: {entry['actor_type']} ({entry['actor_username']})")
    else:
        print(f"   ❌ Failed to get order timeline: {response.text}")

    # Test 7: Test spam prevention
    print("\n7. 🛡️ Testing Spam Prevention...")
    spam_data = dish_addition_data.copy()  # Try to create same update again
    response = requests.post(f"{API_BASE}/order-update", json=spam_data)
    if response.status_code == 400:
        print("   ✅ Spam prevention working - duplicate update blocked")
    else:
        print(f"   ⚠️ Spam prevention may not be working: {response.status_code}")

    # Test 8: Check orders with updates
    print("\n8. 📦 Checking Orders with Update Counts...")
    response = requests.get(f"{API_BASE}/orders/customer/customer1/with-updates")
    if response.status_code == 200:
        orders = response.json().get('orders', [])
        for order in orders[:2]:  # Show first 2 orders
            print(f"   📋 Order {order['id']}: {order['update_count']} updates, {order['unread_notifications']} unread notifications")
            print(f"      Status: {order['current_status_remarks']}")
    else:
        print(f"   ❌ Failed to get orders with updates: {response.text}")

def test_grab_express_updates():
    """Test Grab Express specific updates"""
    print("\n\n🚚 Testing Grab Express Vehicle Upgrades...")

    # Vehicle upgrade for fragile package
    vehicle_upgrade_data = {
        "order_id": "GE001",
        "actor_type": "system",
        "actor_username": "auto_system",
        "update_type": "vehicle_upgraded",
        "details": {
            "old_vehicle": "bike",
            "new_vehicle": "car",
            "reason": "fragile electronics detected"
        }
    }

    response = requests.post(f"{API_BASE}/order-update", json=vehicle_upgrade_data)
    if response.status_code == 200:
        print("   ✅ Vehicle upgrade notification created")
    else:
        print(f"   ❌ Failed to create vehicle upgrade: {response.text}")

if __name__ == "__main__":
    try:
        test_cross_actor_updates()
        test_grab_express_updates()

        print("\n🎉 All tests completed!")
        print("\n💡 Next Steps:")
        print("   1. Start the Flask server: python app.py")
        print("   2. Open frontend: npm start")
        print("   3. Login as 'customer1' to see notifications")
        print("   4. Check order timeline by clicking 'Timeline' button")
        print("   5. Login as different user types to see cross-actor notifications")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Please start the Flask server first:")
        print("   cd GrabHack && python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)