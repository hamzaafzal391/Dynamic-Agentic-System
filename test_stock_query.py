#!/usr/bin/env python3

from router.agent_router import agent_router
from agents.personas import PersonaType

def test_stock_query():
    print("🧪 Testing Stock Query...")
    print("=" * 50)
    
    query = "What is the current stock price of AAPL?"
    print(f"Query: {query}")
    print(f"Persona: Financial")
    print("-" * 30)
    
    try:
        result = agent_router.process_query(query, PersonaType.FINANCIAL)
        
        print("✅ Query processed successfully!")
        print(f"Response: {result['response']}")
        print(f"Success: {result['success']}")
        
        if result.get('sql_results'):
            print("\n📊 SQL Results:")
            for key, value in result['sql_results'].items():
                print(f"  {key}: {value}")
        
        if result.get('error'):
            print(f"\n❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_query() 