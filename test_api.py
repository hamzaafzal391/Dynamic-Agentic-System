#!/usr/bin/env python3

import requests
import json

def test_stock_query():
    print("🧪 Testing Stock Query via API...")
    print("=" * 50)
    
    url = "http://localhost:8000/query"
    data = {
        "query": "What is the current stock price of AAPL?",
        "persona_type": "financial"
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Success: {result.get('success', False)}")
            
            if result.get('sql_results'):
                print("\n📊 SQL Results:")
                for key, value in result['sql_results'].items():
                    print(f"  {key}: {value}")
            else:
                print("\n❌ No SQL results found!")
            
            if result.get('math_results'):
                print("\n🧮 Math Results:")
                for key, value in result['math_results'].items():
                    print(f"  {key}: {value}")
            
            if result.get('documents'):
                print(f"\n📄 Documents: {len(result['documents'])} found")
            
            if result.get('suggested_queries'):
                print(f"\n💡 Suggested Queries: {result['suggested_queries']}")
                
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_stock_query() 