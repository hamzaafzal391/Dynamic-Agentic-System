#!/usr/bin/env python3
"""
Comprehensive backend test script to check all functionalities.
"""

import requests
import json
import time
from typing import Dict, Any

class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, response: Dict[str, Any] = None, error: str = None):
        """Log test results."""
        result = {
            "test": test_name,
            "success": success,
            "response": response,
            "error": error,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
        if response and not success:
            print(f"   Response: {json.dumps(response, indent=2)}")
        print()
    
    def test_health_check(self):
        """Test the root health check endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, data)
            else:
                self.log_test("Health Check", False, {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Health Check", False, error=str(e))
    
    def test_personas(self):
        """Test the personas endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/personas")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Personas", True, data)
            else:
                self.log_test("Get Personas", False, {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Get Personas", False, error=str(e))
    
    def test_datasets(self):
        """Test the datasets endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/datasets")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Datasets", True, data)
            else:
                self.log_test("Get Datasets", False, {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Get Datasets", False, error=str(e))
    
    def test_system_status(self):
        """Test the system status endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Status", True, data)
            else:
                self.log_test("System Status", False, {"status_code": response.status_code})
        except Exception as e:
            self.log_test("System Status", False, error=str(e))
    
    def test_query_endpoint(self):
        """Test the main query endpoint with different types of queries."""
        test_queries = [
            {
                "name": "Math Query",
                "query": "What is 25 * 4 + 10?",
                "persona": "general"
            },
            {
                "name": "Stock Query", 
                "query": "Show me stock data for AAPL",
                "persona": "financial"
            },
            {
                "name": "General Query",
                "query": "Hello, how are you?",
                "persona": "general"
            }
        ]
        
        for test_query in test_queries:
            try:
                payload = {
                    "query": test_query["query"],
                    "persona": test_query["persona"]
                }
                response = self.session.post(f"{self.base_url}/query", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Query: {test_query['name']}", True, data)
                else:
                    self.log_test(f"Query: {test_query['name']}", False, {"status_code": response.status_code})
            except Exception as e:
                self.log_test(f"Query: {test_query['name']}", False, error=str(e))
    
    def test_suggested_queries(self):
        """Test the suggested queries endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/suggested-queries")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Suggested Queries", True, data)
            else:
                self.log_test("Suggested Queries", False, {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Suggested Queries", False, error=str(e))
    
    def test_data_processor_directly(self):
        """Test the data processor functionality directly."""
        try:
            from math_ops.data_processor import data_processor
            
            # Test available datasets
            datasets_result = data_processor.get_available_datasets()
            if datasets_result.get("success"):
                self.log_test("Data Processor - Get Datasets", True, datasets_result)
            else:
                self.log_test("Data Processor - Get Datasets", False, datasets_result)
            
            # Test stock statistics
            if datasets_result.get("success") and datasets_result.get("datasets"):
                first_stock = datasets_result["datasets"][0]["name"]
                stats_result = data_processor.get_stock_statistics(first_stock)
                if stats_result.get("success"):
                    self.log_test(f"Data Processor - Stock Stats ({first_stock})", True, stats_result)
                else:
                    self.log_test(f"Data Processor - Stock Stats ({first_stock})", False, stats_result)
            
        except Exception as e:
            self.log_test("Data Processor Tests", False, error=str(e))
    
    def test_math_computation_directly(self):
        """Test the math computation functionality directly."""
        try:
            from math_ops.computation import math_computation
            
            # Test basic math
            result = math_computation.evaluate_expression("25 * 4 + 10")
            if "error" not in result and "result" in result:
                self.log_test("Math Computation - Basic", True, result)
            else:
                self.log_test("Math Computation - Basic", False, result)
            
            # Test statistics
            result = math_computation.calculate_statistics([1, 2, 3, 4, 5])
            if result.get("success"):
                self.log_test("Math Computation - Statistics", True, result)
            else:
                self.log_test("Math Computation - Statistics", False, result)
                
        except Exception as e:
            self.log_test("Math Computation Tests", False, error=str(e))
    
    def test_rag_document_store(self):
        """Test the RAG document store functionality."""
        try:
            from rag.document_store import document_store
            
            # Test adding a document
            test_doc = {
                "content": "This is a test document about artificial intelligence and machine learning.",
                "metadata": {"source": "test", "type": "text"}
            }
            result = document_store.add_document(test_doc["content"], test_doc["metadata"])
            if result.get("success"):
                self.log_test("RAG - Add Document", True, result)
            else:
                self.log_test("RAG - Add Document", False, result)
            
            # Test searching
            search_result = document_store.search_documents("artificial intelligence", top_k=5)
            if search_result.get("success"):
                self.log_test("RAG - Search Documents", True, search_result)
            else:
                self.log_test("RAG - Search Documents", False, search_result)
                
        except Exception as e:
            self.log_test("RAG Tests", False, error=str(e))
    
    def test_agent_router(self):
        """Test the agent router functionality."""
        try:
            from router.agent_router import agent_router
            from agents.personas import PersonaType
            
            # Test routing
            result = agent_router.process_query("What is 25 * 4?", PersonaType.GENERAL)
            if result and result.get("success"):
                self.log_test("Agent Router - Math Query", True, {"response": result["response"]})
            else:
                self.log_test("Agent Router - Math Query", False, result)
                
        except Exception as e:
            self.log_test("Agent Router Tests", False, error=str(e))
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting Backend Tests...")
        print("=" * 50)
        
        # API Endpoint Tests
        print("\n📡 Testing API Endpoints:")
        print("-" * 30)
        self.test_health_check()
        self.test_personas()
        self.test_datasets()
        self.test_system_status()
        self.test_query_endpoint()
        self.test_suggested_queries()
        
        # Direct Module Tests
        print("\n🔧 Testing Core Modules:")
        print("-" * 30)
        self.test_data_processor_directly()
        self.test_math_computation_directly()
        self.test_rag_document_store()
        self.test_agent_router()
        
        # Summary
        print("\n📊 Test Summary:")
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
        
        return passed, total

if __name__ == "__main__":
    tester = BackendTester()
    passed, total = tester.run_all_tests()
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.") 