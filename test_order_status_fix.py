#!/usr/bin/env python3

"""Test script to verify the order status validation fix"""

import sys
import os

# Add the GrabHack directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'GrabHack'))

def test_order_status_validation():
    """Test that order status validation works correctly"""
    
    try:
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        
        print("Testing Order Status Validation Fix")
        print("===================================")
        
        # Initialize AI engine
        ai_engine = EnhancedAgenticAIEngine()
        print("AI Engine initialized")
        
        # Test scenarios
        test_cases = [
            {
                'description': 'Quality complaint for completed grab_food order',
                'function_name': 'handle_quality_issues',
                'service': 'grab_food',
                'user_type': 'customer',
                'username': 'customer1',
                'user_query': 'I received a completed order GF001 and the food was cold',
                'expected': 'should_proceed'  # GF001 is completed
            },
            {
                'description': 'Quality complaint for in_progress grab_food order',
                'function_name': 'handle_quality_issues',
                'service': 'grab_food',
                'user_type': 'customer',
                'username': 'customer1',
                'user_query': 'My order GF002 food quality is bad',
                'expected': 'should_block'  # GF002 is in_progress
            },
            {
                'description': 'Quality complaint without specific order ID (should check most recent)',
                'function_name': 'handle_quality_issues',
                'service': 'grab_food',
                'user_type': 'customer',
                'username': 'customer1',
                'user_query': 'The food I ordered was terrible',
                'expected': 'should_block'  # Most recent is GF002 (in_progress)
            },
            {
                'description': 'Non-quality complaint for in_progress order',
                'function_name': 'handle_delivery_delay',
                'service': 'grab_food',
                'user_type': 'customer',
                'username': 'customer1',
                'user_query': 'My delivery is taking too long',
                'expected': 'should_proceed'  # Delivery delay is allowed for in_progress
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print("-" * 60)
            
            try:
                response = ai_engine.process_complaint(
                    function_name=test_case['function_name'],
                    user_query=test_case['user_query'],
                    service=test_case['service'],
                    user_type=test_case['user_type'],
                    username=test_case['username']
                )
                
                # Check if response indicates blocking
                is_blocked = "hasn't been completed yet" in response or "still being processed" in response
                
                if test_case['expected'] == 'should_block' and is_blocked:
                    print("✅ PASS: Correctly blocked in-progress order quality complaint")
                elif test_case['expected'] == 'should_proceed' and not is_blocked:
                    print("✅ PASS: Correctly allowed complaint to proceed")
                else:
                    print(f"❌ FAIL: Expected {test_case['expected']}, got blocked={is_blocked}")
                
                print(f"Response preview: {response[:200]}...")
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
        
        print("\n" + "=" * 60)
        print("Test completed!")
        
    except Exception as e:
        print(f"Failed to initialize test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_status_validation()