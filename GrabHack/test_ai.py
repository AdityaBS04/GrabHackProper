#!/usr/bin/env python3
"""
Test script to verify AI engine is working
"""

import os
from dotenv import load_dotenv
load_dotenv()

from enhanced_ai_engine import EnhancedAgenticAIEngine

def test_ai_engine():
    """Test the AI engine with a simple complaint"""
    
    print("Testing Enhanced AI Engine...")
    print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")
    
    try:
        ai_engine = EnhancedAgenticAIEngine()
        print("AI Engine initialized successfully")
        
        # Test with a text-only function
        test_query = "I was charged twice for the same order but only received one delivery"
        
        print(f"\nTesting with query: {test_query}")
        print("Function: handle_double_charge (text-only)")
        
        result = ai_engine.process_complaint(
            function_name="handle_double_charge",
            user_query=test_query,
            service="grab_food",
            user_type="customer",
            image_data=None
        )
        
        print("\n" + "="*50)
        print("AI RESPONSE:")
        print("="*50)
        print(result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"Error testing AI engine: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_engine()