#!/usr/bin/env python3
"""
Test direct API call to missing items functionality
"""

import requests
import json

# Test data
test_data = {
    "message": "I need to report missing items from my order",
    "service": "grab_food",
    "user_type": "customer",
    "username": "test_user",
    "conversation_id": "test_conv_123",
    "category": "order_quality",
    "sub_issue": "handle_missing_items",
    "messages": [],
    "order_id": "TEST12345"
}

try:
    # Make API call to chat endpoint
    response = requests.post(
        "http://localhost:8000/api/chat",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error making API call: {e}")