#!/usr/bin/env python3
"""
Test the API directly
"""

import requests
import json

def test_api():
    """Test the complaint API"""
    
    url = "http://localhost:8000/api/complaint"
    
    # Test data
    payload = {
        "service": "grab_food",
        "user_type": "customer", 
        "category": "order_quality_handler",
        "sub_issue": "handle_substitution_issues",
        "description": "I ordered paneer and chicken bowl but only got paneer bowl"
    }
    
    print("Testing API endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            solution = data.get('solution', 'No solution found')
            print(f"\nSolution Length: {len(solution)} characters")
            print(f"Starts with 'Thank you': {solution.startswith('Thank you for your complaint')}")
            
            # Show first 200 chars safely
            print(f"\nFirst 200 chars: {solution[:200]}...")
            
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_api()