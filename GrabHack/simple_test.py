#!/usr/bin/env python3
"""
Simple test to verify database functions are working
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(__file__))

def test_database_content():
    """Test that the database has been populated correctly"""
    db_path = 'grabhack.db'
    
    if not os.path.exists(db_path):
        print("ERROR: Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("DATABASE CONTENT VERIFICATION")
    print("=" * 40)
    
    # Test users with credibility scores
    print("\n1. USERS WITH CREDIBILITY SCORES:")
    cursor.execute("SELECT username, user_type, credibility_score FROM users ORDER BY credibility_score DESC")
    users = cursor.fetchall()
    for username, user_type, score in users[:10]:  # Show first 10
        print(f"  {username} ({user_type}): Score {score}")
    
    # Test orders with payment methods
    print("\n2. ORDERS WITH PAYMENT METHODS:")
    cursor.execute("SELECT id, username, status, payment_method, price FROM orders WHERE service='grab_food' ORDER BY date DESC LIMIT 5")
    orders = cursor.fetchall()
    for order_id, username, status, payment, price in orders:
        print(f"  {order_id}: {username} | {status} | {payment} | ${price}")
    
    # Test complaints for credibility calculation
    print("\n3. COMPLAINTS BY USER:")
    cursor.execute("SELECT username, COUNT(*) as complaint_count FROM complaints GROUP BY username ORDER BY complaint_count DESC")
    complaints = cursor.fetchall()
    for username, count in complaints:
        print(f"  {username}: {count} complaints")
    
    # Test specific user data
    print("\n4. DETAILED USER ANALYSIS:")
    test_users = ['customer1', 'customer2', 'customer3']
    
    for username in test_users:
        # Get user credibility
        cursor.execute("SELECT credibility_score FROM users WHERE username = ?", (username,))
        score = cursor.fetchone()
        
        # Get order stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled,
                AVG(price) as avg_price
            FROM orders 
            WHERE username = ? AND service = 'grab_food' AND user_type = 'customer'
        """, (username,))
        order_stats = cursor.fetchone()
        
        # Get complaint count
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE username = ?", (username,))
        complaint_count = cursor.fetchone()[0]
        
        print(f"\n  {username}:")
        print(f"    Credibility Score: {score[0] if score else 'N/A'}")
        print(f"    Total Orders: {order_stats[0]}")
        print(f"    Completed: {order_stats[1]}")
        print(f"    Cancelled: {order_stats[2]}")
        print(f"    Avg Order Value: ${order_stats[3]:.2f}" if order_stats[3] else "    Avg Order Value: N/A")
        print(f"    Complaints: {complaint_count}")
    
    conn.close()
    print("\n" + "=" * 40)
    print("DATABASE VERIFICATION COMPLETE!")

def test_credibility_calculation():
    """Test credibility calculation logic"""
    print("\nCREDIBILITY CALCULATION TEST")
    print("=" * 30)
    
    # Import the function here to avoid import issues
    import sqlite3
    from datetime import datetime, timedelta
    
    def calculate_credibility(username):
        """Simplified version of credibility calculation"""
        db_path = 'grabhack.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get base score from users table
        cursor.execute("SELECT credibility_score FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        base_score = result[0] if result else 7
        
        # Get order history
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                AVG(price) as avg_order_value
            FROM orders 
            WHERE username = ? AND service = 'grab_food' AND user_type = 'customer'
        """, (username,))
        
        result = cursor.fetchone()
        total_orders, completed_orders, cancelled_orders, avg_order_value = result
        
        # Get recent complaints
        cursor.execute("""
            SELECT COUNT(*) 
            FROM complaints 
            WHERE username = ? AND service = 'grab_food' 
            AND created_at >= datetime('now', '-30 days')
        """, (username,))
        
        recent_complaints = cursor.fetchone()[0]
        
        conn.close()
        
        # Calculate adjusted score
        adjusted_score = base_score
        
        if total_orders > 0:
            completion_rate = completed_orders / total_orders
            cancellation_rate = cancelled_orders / total_orders
            
            if completion_rate >= 0.9:
                adjusted_score += 2
            elif completion_rate >= 0.7:
                adjusted_score += 1
            elif completion_rate < 0.5:
                adjusted_score -= 2
            
            if cancellation_rate > 0.3:
                adjusted_score -= 2
            elif cancellation_rate > 0.2:
                adjusted_score -= 1
        
        if recent_complaints > 5:
            adjusted_score -= 2
        elif recent_complaints > 2:
            adjusted_score -= 1
        
        return max(1, min(10, int(adjusted_score)))
    
    # Test with different users
    test_users = ['customer1', 'customer2', 'customer3', 'john_doe']
    
    for username in test_users:
        score = calculate_credibility(username)
        print(f"{username}: Calculated credibility = {score}/10")

if __name__ == "__main__":
    test_database_content()
    test_credibility_calculation()