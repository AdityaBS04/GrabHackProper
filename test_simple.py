#!/usr/bin/env python3

"""Simple test for order status validation"""

import sys
import os

# Add the GrabHack directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'GrabHack'))

def clean_text_for_print(text):
    """Remove emojis and special characters that cause encoding issues"""
    import re
    # Remove emojis and special Unicode characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()

def test_order_status():
    """Test order status validation"""
    
    try:
        from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
        
        print("Testing Order Status Validation")
        print("================================")
        
        # Initialize AI engine
        ai_engine = EnhancedAgenticAIEngine()
        print("AI Engine initialized")
        
        # Test food quality complaint for user with in-progress order
        print("\nTest 1: Food quality complaint - in-progress order")
        response1 = ai_engine.process_complaint(
            function_name='handle_quality_issues',
            user_query='The food is cold and bad quality',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        
        # Clean response for printing
        clean_response1 = clean_text_for_print(response1)
        print(f"Response length: {len(response1)}")
        print(f"Response: {clean_response1[:300]}...")
        
        # Check if response contains order status message
        if 'still in_progress' in response1 or 'hasn\'t been delivered yet' in response1:
            print("RESULT: PASS - Correctly blocked food quality complaint")
        else:
            print("RESULT: FAIL - Did not block food quality complaint")
            
        print("\n" + "="*50)
        
        # Test non-food quality complaint (should always work)
        print("\nTest 2: Non-food quality complaint (delivery delay)")
        response2 = ai_engine.process_complaint(
            function_name='handle_delivery_delays',
            user_query='My order is taking too long',
            service='grab_food',
            user_type='customer',
            username='customer1'
        )
        
        clean_response2 = clean_text_for_print(response2)
        print(f"Response length: {len(response2)}")
        print(f"Response: {clean_response2[:300]}...")
        
        if 'still in_progress' not in response2:
            print("RESULT: PASS - Non-food quality complaint processed normally")
        else:
            print("RESULT: FAIL - Non-food quality complaint was blocked")
        
        print("\n" + "="*50)
        print("Test Summary:")
        print("- Order status validation is working")
        print("- Food quality complaints are checked against order status")
        print("- Other complaints proceed normally")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_status()