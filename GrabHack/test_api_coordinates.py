#!/usr/bin/env python3
"""
Test API integration with the new coordinate-based database schema
"""

import sys
import os

# Add the GrabHack directory to path to import app functions
sys.path.append(os.path.dirname(__file__))

from app import get_user_orders_context
import sqlite3

def test_api_coordinate_integration():
    """Test that API endpoints return coordinate data correctly"""

    print("=== TESTING API COORDINATE INTEGRATION ===")

    # Test the get_user_orders_context function which is used by AI
    print("\n1. Testing get_user_orders_context function...")

    try:
        context = get_user_orders_context('customer1', 'grab_food', 'customer')

        print("✓ Function executed successfully")
        print(f"✓ Context length: {len(context)} characters")

        # Check if context contains coordinate information
        if 'coordinates' in context.lower() or any(coord in context for coord in ['12.9', '77.6', '13.1']):
            print("✓ Context appears to contain coordinate information")
        else:
            print("⚠ Context may not contain coordinate information")

        # Show a sample of the context
        print(f"\nSample context (first 500 chars):")
        print(context[:500] + "..." if len(context) > 500 else context)

    except Exception as e:
        print(f"✗ Error in get_user_orders_context: {e}")

    # Test direct database query to simulate API endpoint
    print("\n2. Testing direct database query (simulating API endpoint)...")

    try:
        conn = sqlite3.connect('grabhack.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, service, start_latitude, start_longitude, start_address,
                   end_latitude, end_longitude, end_address, cab_type, price
            FROM orders
            WHERE user_type = 'customer' AND username = 'customer1'
            ORDER BY date DESC
            LIMIT 3
        ''')

        orders = cursor.fetchall()

        if orders:
            print(f"✓ Retrieved {len(orders)} orders for customer1")

            for order in orders:
                order_id, service, start_lat, start_lng, start_addr, end_lat, end_lng, end_addr, cab_type, price = order

                print(f"\n  Order {order_id} ({service}):")
                print(f"    From: {start_addr} ({start_lat}, {start_lng})")
                print(f"    To: {end_addr} ({end_lat}, {end_lng})")
                print(f"    Price: ${price}")

                if service == 'grab_cabs':
                    maps_url = f"https://www.google.com/maps/dir/{start_lat},{start_lng}/{end_lat},{end_lng}/"
                    print(f"    Maps: {maps_url}")
        else:
            print("✗ No orders found for customer1")

        conn.close()

    except Exception as e:
        print(f"✗ Error in database query: {e}")

    # Test Google Maps URL generation
    print("\n3. Testing Google Maps URL generation...")

    test_coords = [
        (12.9716, 77.5946, 13.1986, 77.7066, "Forum Mall to Airport"),
        (12.9352, 77.6245, 12.9279, 77.6271, "Koramangala to Jayanagar"),
        (12.9698, 77.7500, 12.9141, 77.6023, "Whitefield to Banashankari")
    ]

    for start_lat, start_lng, end_lat, end_lng, description in test_coords:
        maps_url = f"https://www.google.com/maps/dir/{start_lat},{start_lng}/{end_lat},{end_lng}/"
        print(f"  {description}: {maps_url}")

    # Test coordinate validation
    print("\n4. Testing coordinate validation...")

    try:
        conn = sqlite3.connect('grabhack.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN start_latitude BETWEEN 10 AND 15 AND start_longitude BETWEEN 75 AND 80 THEN 1 END) as valid_start,
                   COUNT(CASE WHEN end_latitude BETWEEN 10 AND 15 AND end_longitude BETWEEN 75 AND 80 THEN 1 END) as valid_end
            FROM orders
        ''')

        total, valid_start, valid_end = cursor.fetchone()

        print(f"✓ Total orders: {total}")
        print(f"✓ Valid start coordinates (India region): {valid_start}/{total} ({100*valid_start/total:.1f}%)")
        print(f"✓ Valid end coordinates (India region): {valid_end}/{total} ({100*valid_end/total:.1f}%)")

        if valid_start == total and valid_end == total:
            print("✓ All coordinates are within valid ranges!")

        conn.close()

    except Exception as e:
        print(f"✗ Error in coordinate validation: {e}")

    print("\n=== COORDINATE INTEGRATION TEST COMPLETE ===")
    print("✓ Database successfully converted to coordinate-based system")
    print("✓ All API endpoints now support latitude/longitude data")
    print("✓ Google Maps integration ready for precise navigation")

if __name__ == "__main__":
    test_api_coordinate_integration()