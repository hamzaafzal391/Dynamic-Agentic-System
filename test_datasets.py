#!/usr/bin/env python3
"""
Test script to debug the datasets endpoint.
"""

import requests
import json

def test_datasets_endpoint():
    """Test the datasets endpoint directly."""
    try:
        print("Testing /datasets endpoint...")
        response = requests.get("http://localhost:8000/datasets")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Response: {json.dumps(data, indent=2)}")
        else:
            print("Failed to get datasets")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_datasets_endpoint() 