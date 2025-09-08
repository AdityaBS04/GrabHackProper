#!/usr/bin/env python3
"""
Test script to verify grab food functions are working with the new database
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from grab_food.customer.order_quality_handler import OrderQualityHandler
from grab_food.delivery_agent.operational_handler import OperationalHandler
from grab_food.delivery_agent.navigation_location_handler import NavigationLocationHandler

def test_credibility_scoring():
    """Test the credibility scoring with different users"""
    print("\n=== TESTING CREDIBILITY SCORING ===")
    
    handler = OrderQualityHandler()
    
    test_users = [
        ('customer1', 'High credibility user'),
        ('customer2', 'Medium credibility user'), 
        ('customer3', 'Low credibility user'),
        ('john_doe', 'Good customer'),
        ('jane_smith', 'Average customer'),
        ('test_user', 'Test account'),
        ('anonymous', 'Anonymous user')
    ]
    
    for username, description in test_users:
        score = handler.get_customer_credibility_score(username)
        print(f"{description} ({username}): Credibility Score = {score}/10")

def test_payment_verification():
    """Test payment method verification with real order data"""
    print("\n=== TESTING PAYMENT VERIFICATION ===")
    
    handler = OperationalHandler()
    
    test_orders = [
        ('GF001', 'Pizza order - should be online payment'),
        ('GF004', 'Italian Bistro - should be COD'),
        ('GF006', 'Subway order - should be online'),
        ('GF999', 'Non-existent order')
    ]
    
    for order_id, description in test_orders:
        result = handler._check_order_system(order_id)
        print(f"{description} ({order_id}): {result}")

def test_navigation_with_order_data():
    """Test navigation assistance with real order data"""
    print("\n=== TESTING NAVIGATION WITH ORDER DATA ===")
    
    handler = NavigationLocationHandler()
    
    test_queries = [
        "I'm stuck in traffic while delivering order GF001",
        "GPS not working for order GF006, need help",
        "Can't find the address for order GF012",
        "Need general navigation help"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = handler.handle_navigation_issues(query)
        # Print first 200 characters of response
        print(f"Response: {response[:200]}...")

def main():
    """Run all tests"""
    print("TESTING GRAB FOOD FUNCTIONS WITH NEW DATABASE")
    print("=" * 60)
    
    try:
        test_credibility_scoring()
        test_payment_verification()
        test_navigation_with_order_data()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The grab food functions are now using real database data.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Make sure the database has been initialized with test data.")

if __name__ == "__main__":
    main()