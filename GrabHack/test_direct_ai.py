#!/usr/bin/env python3
"""
Direct test of AI engine without handler wrapper
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from enhanced_ai_engine import EnhancedAgenticAIEngine

def test_direct_ai():
    """Test AI engine directly"""
    try:
        print("Testing Direct AI Engine...")
        
        ai_engine = EnhancedAgenticAIEngine()
        print("AI Engine initialized")
        
        # Test with substitution issues (text-only)
        query = "I ordered panner and chicken bowl but only got paneer bowl"
        print(f"Query: {query}")
        print("Function: handle_substitution_issues")
        
        result = ai_engine.process_complaint(
            function_name="handle_substitution_issues",
            user_query=query,
            service="grab_food",
            user_type="customer",
            image_data=None
        )
        
        print("\n" + "="*60)
        print("DIRECT AI RESPONSE:")
        print("="*60)
        
        # Check if result is valid without printing (due to Unicode issues)
        if result and len(result) > 100:
            print("AI Response Generated Successfully!")
            print(f"Response length: {len(result)} characters")
            print(f"Contains 'Thank you': {'Thank you' in result}")
            print(f"Contains 'compensation': {'compensation' in result.lower()}")
            print(f"Contains 'refund': {'refund' in result.lower()}")
        else:
            print("AI Response seems invalid or too short")
            
        print("="*60)
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_direct_ai()
    if result:
        print(f"\nResult length: {len(result)} characters")
        print(f"Starts with generic message: {result.startswith('Thank you for your complaint')}")