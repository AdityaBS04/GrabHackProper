#!/usr/bin/env python3

"""Setup test database with orders for validation testing"""

import sqlite3
import os

def setup_test_database():
    """Create orders table and insert test data"""
    
    # Connect to database
    db_path = os.path.join('GrabHack', 'grab_service.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            user_type TEXT NOT NULL,
            service TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert test orders
    test_orders = [
        # Completed order GF001 
        ('GF001', 'customer1', 'customer', 'grab_food', 'completed', 
         'Biryani from Paradise Restaurant - delivered successfully'),
        
        # In-progress order GF002
        ('GF002', 'customer1', 'customer', 'grab_food', 'in_progress',
         'Pizza from Dominos - currently being delivered'),
        
        # Another completed order for testing
        ('GF003', 'customer1', 'customer', 'grab_food', 'completed',
         'Burger from McDonalds - delivered'),
        
        # Different customer orders
        ('GM001', 'customer2', 'customer', 'grab_mart', 'completed',
         'Grocery items - delivered'),
        
        ('GC001', 'customer2', 'customer', 'grab_car', 'completed',
         'Trip from Airport to Hotel - completed')
    ]
    
    # Insert test data
    cursor.executemany('''
        INSERT OR REPLACE INTO orders 
        (id, username, user_type, service, status, details) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', test_orders)
    
    conn.commit()
    
    # Verify data was inserted
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    
    print(f"Database setup complete! Inserted {len(orders)} test orders:")
    for order in orders:
        print(f"  - {order[0]}: {order[4]} ({order[3]})")
    
    conn.close()

if __name__ == "__main__":
    setup_test_database()