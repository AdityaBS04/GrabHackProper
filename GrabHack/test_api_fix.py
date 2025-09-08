#!/usr/bin/env python3
"""
Test the API fix for JSON parsing issue
"""

import requests
import json

def test_orders_api():
    """Test the orders API endpoint"""
    try:
        # Test the endpoint that was failing
        url = "http://127.0.0.1:5000/api/orders/customer/customer1"
        
        print("Testing orders API endpoint...")
        print(f"URL: {url}")
        
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            print(f"✅ Success! Retrieved {len(orders)} orders")
            
            # Print first order details
            if orders:
                first_order = orders[0]
                print(f"\nFirst Order Details:")
                print(f"  ID: {first_order.get('id')}")
                print(f"  Service: {first_order.get('service')}")
                print(f"  Status: {first_order.get('status')}")
                print(f"  Payment Method: {first_order.get('payment_method')}")
                print(f"  Price: ${first_order.get('price')}")
                print(f"  Details: {first_order.get('details')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask server")
        print("Make sure the Flask app is running with: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_orders_api()