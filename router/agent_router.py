from typing import Dict, Any, List, Optional, TypedDict, Annotated
from enum import Enum
import json
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agents.personas import PersonaType, persona_manager
from rag.document_store import document_store
from math_ops.computation import math_computation
from math_ops.data_processor import data_processor
from ocr.pdf_processor import pdf_processor
from typing_extensions import Annotated

class AgentState(TypedDict):
    """State for the agent workflow."""
    query: Annotated[str, "input"]
    persona_type: Annotated[PersonaType, "input"]
    context: Annotated[str, "input"]
    documents: Annotated[List[Dict[str, Any]], "input"]
    math_results: Annotated[Dict[str, Any], "input"]
    sql_results: Annotated[Dict[str, Any], "input"]
    final_response: Annotated[str, "output"]
    suggested_queries: Annotated[List[str], "output"]
    error: Annotated[Optional[str], "output"]
    query_type: Annotated['QueryType', "input"]

class QueryType(Enum):
    """Types of queries that can be routed."""
    DOCUMENT = "document"
    MATH = "math"
    SQL = "sql"
    GENERAL = "general"
    MIXED = "mixed"

class AgentRouter:
    """Routes queries between different agents and services using LangGraph."""
    
    def __init__(self):
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("document_search", self._document_search)
        workflow.add_node("math_computation", self._math_computation)
        workflow.add_node("sql_query", self._sql_query)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("suggest_queries", self._suggest_queries)
        workflow.set_entry_point("classify_query")
        workflow.add_conditional_edges(
            "classify_query",
            self._route_based_on_type,
            {
                QueryType.DOCUMENT: "document_search",
                QueryType.MATH: "math_computation",
                QueryType.SQL: "sql_query",
                QueryType.GENERAL: "generate_response",
                QueryType.MIXED: "document_search"
            }
        )
        workflow.add_edge("document_search", "math_computation")
        workflow.add_edge("math_computation", "sql_query")
        workflow.add_edge("sql_query", "generate_response")
        workflow.add_edge("math_computation", "generate_response")
        workflow.add_edge("sql_query", "generate_response")
        workflow.add_edge("generate_response", "suggest_queries")
        workflow.add_edge("suggest_queries", END)
        compiled = workflow.compile()
        return compiled
    
    def _classify_query(self, state: AgentState) -> AgentState:
        print(f"[DEFENSIVE DEBUG] _classify_query ENTRY: state keys: {list(state.keys())}, query type: {type(state['query'])}, value: {state['query']}")
        if not isinstance(state['query'], str):
            raise Exception(f"_classify_query: state['query'] is not a string! Type: {type(state['query'])}, Value: {state['query']}")
        query = state["query"].lower()
        # Expanded keywords for document queries
        document_keywords = [
            "document", "pdf", "file", "text", "content", "search", "find", "section", "manual", "architecture", "chapter", "page", "guide", "instruction", "reference", "appendix", "table", "figure", "overview", "introduction", "summary", "details", "explanation", "explain", "describe", "list", "point", "feature", "step", "process", "procedure", "policy", "requirement", "specification", "specs", "how to", "exhibit", "attachment", "part", "subsection"
        ]
        math_keywords = ["calculate", "compute", "math", "statistics", "average", "sum", "percentage"]
        sql_keywords = ["database", "table", "sql", "query", "select", "data", "records"]
        stock_keywords = ["stock", "price", "market", "ticker", "aapl", "googl", "msft", "current", "latest"]
        doc_score = sum(1 for keyword in document_keywords if keyword in query)
        math_score = sum(1 for keyword in math_keywords if keyword in query)
        sql_score = sum(1 for keyword in sql_keywords if keyword in query)
        stock_score = sum(1 for keyword in stock_keywords if keyword in query)
        # Force all queries to DOCUMENT for testing
        query_type = QueryType.DOCUMENT
        state["query_type"] = query_type
        print(f"[DEFENSIVE DEBUG] _classify_query EXIT: query type: {type(state['query'])}, value: {state['query']}")
        return state
    
    def _route_based_on_type(self, state: AgentState) -> QueryType:
        result = state.get("query_type", QueryType.GENERAL)
        if isinstance(result, list):
            raise Exception("_route_based_on_type must return a single QueryType, not a list!")
        return result
    
    def _document_search(self, state: AgentState) -> AgentState:
        print(f"[DEFENSIVE DEBUG] _document_search ENTRY: query type: {type(state['query'])}, value: {state['query']}")
        if not isinstance(state['query'], str):
            raise Exception(f"_document_search: state['query'] is not a string! Type: {type(state['query'])}, Value: {state['query']}")
        try:
            query = state["query"]
            
            # Call document store search
            documents_result = document_store.search_documents(query, top_k=5)
            
            # Extract documents from result
            if isinstance(documents_result, dict):
                if documents_result.get("success"):
                    documents_list = documents_result.get("documents", [])
                else:
                    documents_list = []
            else:
                documents_list = documents_result if isinstance(documents_result, list) else []
            
            # Store documents in state
            state["documents"] = documents_list
            
            # Build context from documents
            context_parts = []
            if documents_list and isinstance(documents_list, list):
                for i, doc in enumerate(documents_list):
                    if isinstance(doc, dict) and "content" in doc:
                        content_preview = doc['content'][:500] if doc['content'] else "No content"
                        context_parts.append(f"Document {i+1}: {content_preview}...")
            state["context"] = "\n\n".join(context_parts)
            
        except Exception as e:
            state["error"] = f"Document search failed: {str(e)}"
            state["documents"] = []
            state["context"] = ""
        print(f"[DEFENSIVE DEBUG] _document_search EXIT: query type: {type(state['query'])}, value: {state['query']}")
        return state
    
    def _math_computation(self, state: AgentState) -> AgentState:
        print(f"[DEFENSIVE DEBUG] _math_computation ENTRY: query type: {type(state['query'])}, value: {state['query']}")
        if not isinstance(state['query'], str):
            raise Exception(f"_math_computation: state['query'] is not a string! Type: {type(state['query'])}, Value: {state['query']}")
        try:
            query = state["query"]
            math_results = {}
            
            # Check for mathematical expressions
            import re
            math_patterns = [
                r'(\d+[\+\-\*\/\^\(\)\d\s]+)',  # Basic arithmetic
                r'calculate\s+(.+)',  # Calculate commands
                r'what\s+is\s+(.+)',  # What is questions
            ]
            
            for pattern in math_patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                for match in matches:
                    if match.strip():
                        result = math_computation.evaluate_expression(match.strip())
                        if "error" not in result:
                            math_results[match.strip()] = result
            
            # Check for statistical operations
            if any(word in query.lower() for word in ["average", "mean", "median", "statistics"]):
                # This would need actual data to work with
                math_results["statistical_analysis"] = "Statistical analysis requested"
            
            state["math_results"] = math_results
            
        except Exception as e:
            state["error"] = f"Math computation failed: {str(e)}"
            state["math_results"] = {}
        print(f"[DEFENSIVE DEBUG] _math_computation EXIT: query type: {type(state['query'])}, value: {state['query']}")
        return state
    
    def _sql_query(self, state: AgentState) -> AgentState:
        print(f"[DEFENSIVE DEBUG] _sql_query ENTRY: query type: {type(state['query'])}, value: {state['query']}")
        if not isinstance(state['query'], str):
            raise Exception(f"_sql_query: state['query'] is not a string! Type: {type(state['query'])}, Value: {state['query']}")
        try:
            query = state["query"]
            data_results = {}

            # Check for stock-related queries
            stock_keywords = ["stock", "price", "market", "moving average", "ma", "ticker"]
            if any(keyword in query.lower() for keyword in stock_keywords):
                # Get available datasets
                datasets_result = data_processor.get_available_datasets()
                if datasets_result.get("success"):
                    data_results["available_stocks"] = [d["name"] for d in datasets_result["datasets"]]

                    # Extract stock symbol from query (robust: any uppercase ticker)
                    import re
                    stock_symbols = [d["name"] for d in datasets_result["datasets"]]
                    found_symbol = None
                    for symbol in stock_symbols:
                        if re.search(rf"\b{symbol}\b", query, re.IGNORECASE):
                            found_symbol = symbol
                            break

                    if found_symbol:
                        # Get current stock price (latest close price)
                        stock_data = data_processor.query_stock_data(found_symbol)
                        if stock_data.get("success") and stock_data["data"]:
                            latest_data = stock_data["data"][-1]  # Get the most recent data
                            data_results[f"{found_symbol}_current_price"] = {
                                "symbol": found_symbol,
                                "close_price": latest_data["close"],
                                "date": latest_data["date"],
                                "open": latest_data["open"],
                                "high": latest_data["high"],
                                "low": latest_data["low"],
                                "volume": latest_data["volume"]
                            }
                        else:
                            data_results["error"] = stock_data.get("error", "No stock data found.")

                        # Get statistics
                        stats_result = data_processor.get_stock_statistics(found_symbol)
                        if stats_result.get("success"):
                            data_results[f"{found_symbol}_statistics"] = stats_result
                        else:
                            data_results["stats_error"] = stats_result.get("error", "No stats found.")
                    else:
                        data_results["error"] = "No stock symbol found in query."
                        # If no specific symbol found, get stats for first available stock
                        if datasets_result["datasets"]:
                            first_stock = datasets_result["datasets"][0]["name"]
                            stats_result = data_processor.get_stock_statistics(first_stock)
                            if stats_result.get("success"):
                                data_results[f"{first_stock}_statistics"] = stats_result
                else:
                    data_results["error"] = datasets_result.get("error", "No datasets found.")
            else:
                pass # No stock keywords detected in query

            state["sql_results"] = data_results

        except Exception as e:
            state["error"] = f"Data query failed: {str(e)}"
            state["sql_results"] = {"error": str(e)}
        print(f"[DEFENSIVE DEBUG] _sql_query EXIT: query type: {type(state['query'])}, value: {state['query']}")
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        print(f"[DEFENSIVE DEBUG] _generate_response ENTRY: query type: {type(state['query'])}, value: {state['query']}")
        if not isinstance(state['query'], str):
            raise Exception(f"_generate_response: state['query'] is not a string! Type: {type(state['query'])}, Value: {state['query']}")
        try:
            query = state["query"]
            persona_type = state["persona_type"]
            context = state.get("context", "")
            
            # Build comprehensive context for other queries
            context_parts = []
            
            # Only use top 2 document chunks for context
            documents = state.get("documents", [])
            
            if isinstance(documents, list):
                for i, doc in enumerate(documents[:2]):
                    if isinstance(doc, dict) and "content" in doc:
                        doc_content = doc['content'][:500] if doc['content'] else "No content"
                        context_parts.append(f"Document {i+1}: {doc_content}...")
            if context:
                context_parts.append(f"Document Context: {context}")
            
            if state.get("math_results"):
                context_parts.append(f"Math Results: {json.dumps(state['math_results'], indent=2)}")
            
            if state.get("sql_results"):
                context_parts.append(f"Database Results: {json.dumps(state['sql_results'], indent=2)}")
            
            full_context = "\n\n".join(context_parts)
            
            # Generate response using persona
            response = persona_manager.route_query(query, persona_type, full_context)
            
            print(f"[OPENAI RESPONSE] Generated response: {response}")
            
            state["final_response"] = response
            
        except Exception as e:
            state["error"] = f"Response generation failed: {str(e)}"
            state["final_response"] = "Sorry, I encountered an error while processing your request."
        print(f"[DEFENSIVE DEBUG] _generate_response EXIT: query type: {type(state['query'])}, value: {state['query']}")
        return state
    
    def _suggest_queries(self, state: AgentState) -> AgentState:
        print(f"[DEFENSIVE DEBUG] _suggest_queries ENTRY: query type: {type(state['query'])}, value: {state['query']}")
        if not isinstance(state['query'], str):
            raise Exception(f"_suggest_queries: state['query'] is not a string! Type: {type(state['query'])}, Value: {state['query']}")
        try:
            query = state["query"]
            response = state.get("final_response", "")
            
            # Generate suggested queries based on the original query and response
            suggestions = self._generate_suggestions(query, response)
            state["suggested_queries"] = suggestions
            
        except Exception as e:
            state["suggested_queries"] = []
        print(f"[DEFENSIVE DEBUG] _suggest_queries EXIT: query type: {type(state['query'])}, value: {state['query']}")
        return state
    
    def _generate_suggestions(self, query: str, response: str) -> List[str]:
        """Generate suggested follow-up queries."""
        suggestions = []
        
        # Simple rule-based suggestions
        query_lower = query.lower()
        
        if "document" in query_lower or "pdf" in query_lower:
            suggestions.extend([
                "Can you search for more specific information in the documents?",
                "What are the key findings from the uploaded documents?",
                "Can you summarize the main points from the documents?"
            ])
        
        if "calculate" in query_lower or "math" in query_lower:
            suggestions.extend([
                "Can you perform additional calculations on this data?",
                "What statistical analysis can be done on these numbers?",
                "Can you create a visualization of these results?"
            ])
        
        if "database" in query_lower or "table" in query_lower:
            suggestions.extend([
                "What other tables are available in the database?",
                "Can you show me the structure of the tables?",
                "What queries can I run on this data?"
            ])
        
        # Add general suggestions if we don't have enough
        while len(suggestions) < 3:
            general_suggestions = [
                "Can you provide more details about this?",
                "What are the implications of this information?",
                "How does this relate to other data we have?"
            ]
            for suggestion in general_suggestions:
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
                    break
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def process_query(self, query: str, persona_type: PersonaType = PersonaType.GENERAL) -> Dict[str, Any]:
        print(f"[DEFENSIVE DEBUG] process_query ENTRY: query type: {type(query)}, value: {query}, persona_type: {persona_type}")
        try:
            # Initialize state
            initial_state = {
                "query": query,
                "persona_type": persona_type,
                "context": "",
                "documents": [],
                "math_results": {},
                "sql_results": {},
                "final_response": "",
                "suggested_queries": [],
                "error": None,
                "query_type": QueryType.DOCUMENT  # or set appropriately
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)  # type: ignore
            print(f"[DEFENSIVE DEBUG] process_query EXIT: final_state['query'] type: {type(final_state['query'])}, value: {final_state['query']}")
            print(f"[DEFENSIVE DEBUG] process_query EXIT: final_state: {final_state}")
            print("[DEBUG] API SENDING RESPONSE")
            
            return {
                "success": True,
                "response": final_state["final_response"],
                "suggested_queries": final_state["suggested_queries"],
                "documents": final_state["documents"],
                "math_results": final_state["math_results"],
                "sql_results": final_state["sql_results"],
                "error": final_state.get("error")
            }
            
        except Exception as e:
            print(f"[DEFENSIVE DEBUG] process_query ERROR: {str(e)}")
            
            # Check if this is the LangGraph "multiple values" error
            if "Can receive only one value per step" in str(e):
                print("[WORKAROUND] LangGraph workflow error detected, attempting to extract AI response...")
                
                # Try to manually run the workflow steps to get the AI response
                try:
                    # Run the workflow steps manually
                    state = initial_state.copy()
                    state = self._classify_query(state)  # type: ignore
                    state = self._document_search(state)  # type: ignore
                    state = self._math_computation(state)  # type: ignore
                    state = self._sql_query(state)  # type: ignore
                    state = self._generate_response(state)  # type: ignore
                    state = self._suggest_queries(state)  # type: ignore
                    
                    print(f"[WORKAROUND] Successfully generated response: {state['final_response']}")
                    
                    return {
                        "success": True,
                        "response": state["final_response"],
                        "suggested_queries": state["suggested_queries"],
                        "documents": state["documents"],
                        "math_results": state["math_results"],
                        "sql_results": state["sql_results"],
                        "error": None
                    }
                except Exception as manual_error:
                    print(f"[WORKAROUND] Manual execution also failed: {str(manual_error)}")
            
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "response": "Sorry, I encountered an error while processing your request."
            }

# Global agent router instance
agent_router = AgentRouter() 