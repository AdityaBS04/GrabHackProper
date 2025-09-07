#!/usr/bin/env python3
"""
Complete test of the chatbot functionality with image requests
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'GrabHack'))

from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

def test_conversation_flow():
    """Test the complete conversation flow"""
    print("Testing chatbot conversation flow...")
    
    ai_engine = EnhancedAgenticAIEngine()
    
    # Test 1: Initial query about food quality issue
    print("\n=== Test 1: Food Quality Issue (should request image) ===")
    
    conversation_history = [
        {'role': 'user', 'content': 'My food arrived and it looks terrible, completely different from what I ordered'}
    ]
    
    response = ai_engine.process_conversation(
        message="My food arrived and it looks terrible, completely different from what I ordered",
        service="grab_food",
        user_type="customer", 
        conversation_history=conversation_history,
        session_context={}
    )
    
    print(f"Response: {response.get('text', '')[:200]}...")
    print(f"Requires Image: {response.get('requires_image', False)}")
    print(f"Image Request: {response.get('image_request', 'None')}")
    
    # Test 2: Text-only issue
    print("\n=== Test 2: Payment Issue (should not request image) ===")
    
    conversation_history = [
        {'role': 'user', 'content': 'I was charged twice for my order but only received it once'}
    ]
    
    response = ai_engine.process_conversation(
        message="I was charged twice for my order but only received it once",
        service="grab_food",
        user_type="customer",
        conversation_history=conversation_history,
        session_context={}
    )
    
    print(f"Response: {response.get('text', '')[:200]}...")
    print(f"Requires Image: {response.get('requires_image', False)}")
    
    # Test 3: General inquiry
    print("\n=== Test 3: General Inquiry (should ask for more details) ===")
    
    conversation_history = [
        {'role': 'user', 'content': 'Hi, I have a problem with my order'}
    ]
    
    response = ai_engine.process_conversation(
        message="Hi, I have a problem with my order",
        service="grab_food", 
        user_type="customer",
        conversation_history=conversation_history,
        session_context={}
    )
    
    print(f"Response: {response.get('text', '')[:200]}...")
    print(f"Requires Image: {response.get('requires_image', False)}")

if __name__ == "__main__":
    test_conversation_flow()