#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'GrabHack'))

def test_order_validation():
    try:
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        
        ai_engine = EnhancedAgenticAIEngine()
        
        # Test 1: Quality complaint for completed order (should proceed)
        print("Test 1: Quality complaint for completed order GF001")
        response1 = ai_engine.process_complaint(
            function_name='handle_quality_issues',
            user_query='My order GF001 had cold food',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        blocked1 = "hasn't been completed yet" in response1
        print(f"Blocked: {blocked1} (should be False)")
        print(f"Response length: {len(response1)} chars\n")
        
        # Test 2: Quality complaint for in-progress order (should block)  
        print("Test 2: Quality complaint for in-progress order GF002")
        response2 = ai_engine.process_complaint(
            function_name='handle_quality_issues',
            user_query='My order GF002 has bad quality',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        blocked2 = "hasn't been completed yet" in response2
        print(f"Blocked: {blocked2} (should be True)")
        print(f"Response length: {len(response2)} chars\n")
        
        # Test 3: Non-quality complaint for in-progress order (should proceed)
        print("Test 3: Delivery delay complaint for in-progress order")
        response3 = ai_engine.process_complaint(
            function_name='handle_delivery_delay',
            user_query='My delivery is taking too long',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        blocked3 = "hasn't been completed yet" in response3
        print(f"Blocked: {blocked3} (should be False)")
        print(f"Response length: {len(response3)} chars")
        
        print("\nSUMMARY:")
        print(f"Test 1 (completed order quality): {'PASS' if not blocked1 else 'FAIL'}")
        print(f"Test 2 (in-progress order quality): {'PASS' if blocked2 else 'FAIL'}")
        print(f"Test 3 (in-progress order non-quality): {'PASS' if not blocked3 else 'FAIL'}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_validation()