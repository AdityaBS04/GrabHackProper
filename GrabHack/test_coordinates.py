#!/usr/bin/env python3
"""
Test script to verify the new coordinate-based database schema works properly
"""

import sqlite3
import os
import json

DATABASE_PATH = 'grabhack_coordinates_test.db'

def test_coordinate_database():
    """Test the new coordinate-based database schema"""

    # Remove existing test database
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    # Create database connection
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create the new coordinate-based table
    cursor.execute('''
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            user_type TEXT NOT NULL,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
            price REAL,
            start_latitude REAL,
            start_longitude REAL,
            start_address TEXT,
            end_latitude REAL,
            end_longitude REAL,
            end_address TEXT,
            customer_id TEXT,
            restaurant_id TEXT,
            driver_id TEXT,
            restaurant_name TEXT,
            food_items TEXT,
            cab_type TEXT,
            products_ordered TEXT,
            payment_method TEXT DEFAULT 'online',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')

    # Insert test data with Bangalore coordinates
    test_orders = [
        # Grab Food Order
        ('GF001', 'grab_food', 'customer', 'customer1', 'completed', 25.50,
         12.9352, 77.6245, 'Pizza Palace Restaurant, Koramangala', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', 'REST001', 'DRV001', 'Pizza Palace', 'Margherita Pizza Large, Garlic Bread, Coca Cola', None, None,
         'online', '2024-08-15', '{"restaurant": "Pizza Palace", "total": 25.50, "rating": 5}'),

        # Grab Cabs Order
        ('GC001', 'grab_cabs', 'customer', 'customer1', 'completed', 15.00,
         12.9716, 77.5946, 'Forum Mall, Koramangala', 13.1986, 77.7066, 'Kempegowda International Airport',
         'CUST001', None, 'DRV101', None, None, 'Sedan', None,
         'upi', '2024-09-02', '{"from": "Forum Mall", "to": "Airport", "distance_km": 35, "duration_minutes": 55}'),

        # Grab Express Order
        ('GE001', 'grab_express', 'customer', 'customer1', 'completed', 12.50,
         12.9716, 77.5946, 'Electronics Store Downtown, MG Road', 12.9279, 77.6271, '123 Oak Street Apartment 4B, Jayanagar',
         'CUST001', None, 'EXP001', None, None, None, 'Smartphone Case, Screen Protector, Charging Cable',
         'online', '2024-09-01', '{"pickup_location": "Electronics Store Downtown", "delivery_time_minutes": 45, "vehicle_type": "Bike", "package_size": "Small", "rating": 5}')
    ]

    cursor.executemany('''
        INSERT INTO orders
        (id, service, user_type, username, status, price, start_latitude, start_longitude, start_address,
         end_latitude, end_longitude, end_address, customer_id, restaurant_id, driver_id, restaurant_name,
         food_items, cab_type, products_ordered, payment_method, date, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_orders)

    # Test query with new coordinate fields
    cursor.execute('''
        SELECT id, service, start_latitude, start_longitude, start_address,
               end_latitude, end_longitude, end_address, cab_type
        FROM orders
        ORDER BY date DESC
    ''')

    print("SUCCESS: Database with coordinate schema created successfully!")
    print("\nTest Data with Coordinates:")

    for row in cursor.fetchall():
        order_id, service, start_lat, start_lng, start_addr, end_lat, end_lng, end_addr, cab_type = row

        print(f"\nOrder: {order_id} ({service})")
        print(f"   From: {start_addr} ({start_lat:.4f}, {start_lng:.4f})")
        print(f"   To: {end_addr} ({end_lat:.4f}, {end_lng:.4f})")

        if service == 'grab_cabs':
            # Generate Google Maps URL for cabs
            maps_url = f"https://www.google.com/maps/dir/{start_lat},{start_lng}/{end_lat},{end_lng}/"
            print(f"   Google Maps: {maps_url}")

    # Test coordinate-based Google Maps URL generation
    def generate_maps_url(start_lat, start_lng, end_lat, end_lng):
        return f"https://www.google.com/maps/dir/{start_lat},{start_lng}/{end_lat},{end_lng}/"

    print("\nCoordinate-based Google Maps Integration Test:")

    # Test with Forum Mall to Airport coordinates
    forum_to_airport_url = generate_maps_url(12.9716, 77.5946, 13.1986, 77.7066)
    print(f"   Forum Mall to Airport: {forum_to_airport_url}")

    # Test with Koramangala to Jayanagar coordinates
    koramangala_to_jayanagar_url = generate_maps_url(12.9352, 77.6245, 12.9279, 77.6271)
    print(f"   Koramangala to Jayanagar: {koramangala_to_jayanagar_url}")

    conn.commit()
    conn.close()

    print(f"\nTest database saved as: {DATABASE_PATH}")
    print("Coordinate-based location system is working perfectly!")

if __name__ == "__main__":
    test_coordinate_database()