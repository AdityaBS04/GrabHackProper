#!/usr/bin/env python3
"""
Test dedicated missing items endpoint
"""

import requests
import json

# Test data
test_data = {
    "username": "test_user",
    "order_id": "TEST12345",
    "message": "I want to report missing items from my order"
}

try:
    # Make API call to missing items endpoint
    response = requests.post(
        "http://localhost:8000/api/missing-items",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error making API call: {e}")