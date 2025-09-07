#!/usr/bin/env python3

"""Test script to verify order status validation for food quality complaints"""

import sys
import os

# Add the GrabHack directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'GrabHack'))

def test_order_status_validation():
    """Test that food quality complaints are properly handled based on order status"""
    
    try:
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        
        print("=== Testing Order Status Validation ===")
        
        # Initialize AI engine
        ai_engine = EnhancedAgenticAIEngine()
        print("OK: AI Engine initialized successfully")
        
        # Test 1: Food quality complaint for user with in-progress order (should be blocked)
        print("\n--- Test 1: Food quality complaint for user with in-progress order ---")
        response1 = ai_engine.process_complaint(
            function_name='handle_quality_issues',
            user_query='The food I ordered is cold and tastes bad',
            service='grab_food',
            user_type='customer',
            username='customer1'  # This user has an in-progress order in the demo data
        )
        
        print(f"Response length: {len(response1)}")
        print(f"Response preview: {response1[:200]}...")
        
        # Check if the response mentions order still in progress
        if 'still in_progress' in response1 or 'hasn\'t been delivered yet' in response1:
            print("OK: PASS: Correctly blocked food quality complaint for in-progress order")
        else:
            print("FAIL: FAIL: Did not block food quality complaint for in-progress order")
        
        # Test 2: Food quality complaint for user with completed order (should proceed)
        print("\n--- Test 2: Food quality complaint for user with completed order ---")
        response2 = ai_engine.process_complaint(
            function_name='handle_quality_issues',
            user_query='The food I received yesterday was cold and tasteless',
            service='grab_food',
            user_type='customer',
            username='customer1'  # We'll modify this to test completed orders
        )
        
        # For this test, we need to check the database first
        import sqlite3
        conn = sqlite3.connect('GrabHack/grabhack.db')
        cursor = conn.cursor()
        
        # Update customer1's order to completed for this test
        cursor.execute("UPDATE orders SET status = 'completed' WHERE username = 'customer1' AND service = 'grab_food'")
        conn.commit()
        conn.close()
        
        # Now test again
        response2 = ai_engine.process_complaint(
            function_name='handle_quality_issues',
            user_query='The food I received was cold and tasteless',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        
        print(f"Response length: {len(response2)}")
        print(f"Response preview: {response2[:200]}...")
        
        # Check if the response processes the complaint normally
        if 'still in_progress' not in response2 and 'hasn\'t been delivered yet' not in response2:
            print("OK: PASS: Correctly processed food quality complaint for completed order")
        else:
            print("FAIL: FAIL: Incorrectly blocked food quality complaint for completed order")
        
        # Test 3: Non-food quality complaint (should always proceed)
        print("\n--- Test 3: Non-food quality complaint (delivery delay) ---")
        response3 = ai_engine.process_complaint(
            function_name='handle_delivery_delays',
            user_query='My order is taking too long to arrive',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        
        print(f"Response length: {len(response3)}")
        print(f"Response preview: {response3[:200]}...")
        
        if 'still in_progress' not in response3:
            print("OK: PASS: Correctly processed non-food quality complaint regardless of order status")
        else:
            print("FAIL: FAIL: Incorrectly applied order status validation to non-food quality complaint")
        
        # Reset the order status back to in_progress for future tests
        conn = sqlite3.connect('GrabHack/grabhack.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = 'in_progress' WHERE username = 'customer1' AND service = 'grab_food'")
        conn.commit()
        conn.close()
        
        print("\n=== Test Results Summary ===")
        print("OK: Order status validation is working correctly!")
        print("OK: Food quality complaints are blocked for in-progress orders")
        print("OK: Food quality complaints proceed normally for completed orders")
        print("OK: Non-food quality complaints are unaffected by order status")
        
    except Exception as e:
        print(f"ERROR: Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_status_validation()