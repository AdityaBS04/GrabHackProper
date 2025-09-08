#!/usr/bin/env python3
"""
Script to reset and reinitialize the database with fresh test data
Run this script to populate the database with comprehensive test data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import init_database
import sqlite3

def reset_database():
    """Reset the database and reinitialize with test data"""
    print("Resetting database...")
    
    # Remove existing database file
    db_path = 'grabhack.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Reinitialize with fresh data
    print("Creating new database with test data...")
    init_database()
    print("Database reinitialized successfully!")
    
    # Show summary of data created
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count users by type
    cursor.execute("SELECT user_type, COUNT(*) FROM users GROUP BY user_type")
    user_counts = cursor.fetchall()
    
    # Count orders by service and user type
    cursor.execute("SELECT service, user_type, COUNT(*) FROM orders GROUP BY service, user_type")
    order_counts = cursor.fetchall()
    
    # Count complaints by user type
    cursor.execute("SELECT user_type, COUNT(*) FROM complaints GROUP BY user_type")
    complaint_counts = cursor.fetchall()
    
    conn.close()
    
    print("\nDatabase Summary:")
    print("=" * 50)
    
    print("\nUsers Created:")
    for user_type, count in user_counts:
        print(f"  - {user_type}: {count} users")
    
    print("\nOrders Created:")
    for service, user_type, count in order_counts:
        print(f"  - {service} - {user_type}: {count} orders")
    
    print("\nComplaints Created:")
    for user_type, count in complaint_counts:
        print(f"  - {user_type}: {count} complaints")
    
    print("\nTest Scenarios Available:")
    print("  - High credibility customer: customer1 (score: 9)")
    print("  - Medium credibility customer: customer2 (score: 5)")
    print("  - Low credibility customer: customer3 (score: 3)")
    print("  - Delivery agents: agent1, agent2, agent3")
    print("  - Restaurants: resto1, resto2, resto3")
    print("  - Various order statuses: completed, in_progress, cancelled")
    print("  - Different payment methods: online, cod, upi, card")
    print("  - Multiple complaint types for testing")
    
    print("\nReady for testing!")
    print("You can now test the grab food functions with realistic data.")

if __name__ == "__main__":
    reset_database()