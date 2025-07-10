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

class AgentState(TypedDict):
    """State for the agent workflow."""
    query: str
    persona_type: PersonaType
    context: str
    documents: List[Dict[str, Any]]
    math_results: Dict[str, Any]
    sql_results: Dict[str, Any]
    final_response: str
    suggested_queries: List[str]
    error: Optional[str]

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
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("document_search", self._document_search)
        workflow.add_node("math_computation", self._math_computation)
        workflow.add_node("sql_query", self._sql_query)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("suggest_queries", self._suggest_queries)
        
        # Define edges
        workflow.set_entry_point("classify_query")
        
        # Add conditional edges based on query type
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
        
        # Add edges for mixed queries
        workflow.add_edge("document_search", "math_computation")
        workflow.add_edge("math_computation", "sql_query")
        workflow.add_edge("sql_query", "generate_response")
        
        # Add edges for single-type queries
        workflow.add_edge("math_computation", "generate_response")
        workflow.add_edge("sql_query", "generate_response")
        
        # Add final steps
        workflow.add_edge("generate_response", "suggest_queries")
        workflow.add_edge("suggest_queries", END)
        
        return workflow.compile()
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Classify the type of query."""
        query = state["query"].lower()
        
        # Keywords for different query types
        document_keywords = ["document", "pdf", "file", "text", "content", "search", "find"]
        math_keywords = ["calculate", "compute", "math", "statistics", "average", "sum", "percentage"]
        sql_keywords = ["database", "table", "sql", "query", "select", "data", "records"]
        stock_keywords = ["stock", "price", "market", "ticker", "aapl", "googl", "msft", "current", "latest"]
        
        doc_score = sum(1 for keyword in document_keywords if keyword in query)
        math_score = sum(1 for keyword in math_keywords if keyword in query)
        sql_score = sum(1 for keyword in sql_keywords if keyword in query)
        stock_score = sum(1 for keyword in stock_keywords if keyword in query)
        
        # Determine query type
        if stock_score > 0:
            query_type = QueryType.SQL  # Stock queries should use data processing
        elif doc_score > 0 and math_score > 0 and sql_score > 0:
            query_type = QueryType.MIXED
        elif doc_score > 0 and (math_score > 0 or sql_score > 0):
            query_type = QueryType.MIXED
        elif doc_score > 0:
            query_type = QueryType.DOCUMENT
        elif math_score > 0:
            query_type = QueryType.MATH
        elif sql_score > 0:
            query_type = QueryType.SQL
        else:
            query_type = QueryType.GENERAL
        
        state["query_type"] = query_type
        return state
    
    def _route_based_on_type(self, state: AgentState) -> QueryType:
        """Route to the appropriate node based on query type."""
        return state.get("query_type", QueryType.GENERAL)
    
    def _document_search(self, state: AgentState) -> AgentState:
        """Search for relevant documents."""
        try:
            query = state["query"]
            documents = document_store.search_documents(query, top_k=5)
            state["documents"] = documents
            
            # Build context from documents
            context_parts = []
            for doc in documents:
                context_parts.append(f"Document: {doc['content'][:500]}...")
            
            state["context"] = "\n\n".join(context_parts)
            
        except Exception as e:
            state["error"] = f"Document search failed: {str(e)}"
            state["documents"] = []
            state["context"] = ""
        
        return state
    
    def _math_computation(self, state: AgentState) -> AgentState:
        """Perform mathematical computations."""
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
        
        return state
    
    def _sql_query(self, state: AgentState) -> AgentState:
        """Execute data queries using CSV files."""
        try:
            query = state["query"]
            data_results = {}
            print(f"[DEBUG] _sql_query received query: {query}")

            # Check for stock-related queries
            stock_keywords = ["stock", "price", "market", "moving average", "ma", "ticker"]
            if any(keyword in query.lower() for keyword in stock_keywords):
                print(f"[DEBUG] Stock keywords detected in query")
                # Get available datasets
                datasets_result = data_processor.get_available_datasets()
                print(f"[DEBUG] Available datasets: {datasets_result}")
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
                    print(f"[DEBUG] Found symbol: {found_symbol}")

                    if found_symbol:
                        # Get current stock price (latest close price)
                        stock_data = data_processor.query_stock_data(found_symbol)
                        print(f"[DEBUG] Stock data for {found_symbol}: {stock_data}")
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
                        print(f"[DEBUG] Stats for {found_symbol}: {stats_result}")
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
                print(f"[DEBUG] No stock keywords detected in query")

            state["sql_results"] = data_results

        except Exception as e:
            state["error"] = f"Data query failed: {str(e)}"
            state["sql_results"] = {"error": str(e)}

        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate final response using the selected persona."""
        try:
            query = state["query"]
            persona_type = state["persona_type"]
            context = state.get("context", "")
            
            # Check if we have stock data and build a specific response
            if state.get("sql_results"):
                stock_data = state["sql_results"]
                
                # Look for current price data
                for key, value in stock_data.items():
                    if "_current_price" in key:
                        symbol = value["symbol"]
                        price = value["close_price"]
                        date = value["date"]
                        
                        if persona_type == PersonaType.FINANCIAL:
                            response = f"Based on the latest available data, {symbol} (Apple Inc.) closed at ${price:.2f} on {date}. "
                            
                            # Add additional context if available
                            if f"{symbol}_statistics" in stock_data:
                                stats = stock_data[f"{symbol}_statistics"]
                                if "price_stats" in stats:
                                    price_stats = stats["price_stats"]["close"]
                                    response += f"Over the available period, {symbol} has ranged from ${price_stats['min']:.2f} to ${price_stats['max']:.2f} with an average closing price of ${price_stats['mean']:.2f}. "
                            
                            response += "Please note that this is historical data and current market prices may differ. For real-time stock prices, please check a financial website or your trading platform."
                            
                            state["final_response"] = response
                            return state
            
            # Build comprehensive context for other queries
            context_parts = []
            
            if context:
                context_parts.append(f"Document Context: {context}")
            
            if state.get("math_results"):
                context_parts.append(f"Math Results: {json.dumps(state['math_results'], indent=2)}")
            
            if state.get("sql_results"):
                context_parts.append(f"Database Results: {json.dumps(state['sql_results'], indent=2)}")
            
            full_context = "\n\n".join(context_parts)
            
            # Generate response using persona
            response = persona_manager.route_query(query, persona_type, full_context)
            state["final_response"] = response
            
        except Exception as e:
            state["error"] = f"Response generation failed: {str(e)}"
            state["final_response"] = "Sorry, I encountered an error while processing your request."
        
        return state
    
    def _suggest_queries(self, state: AgentState) -> AgentState:
        """Generate suggested follow-up queries."""
        try:
            query = state["query"]
            response = state.get("final_response", "")
            
            # Generate suggested queries based on the original query and response
            suggestions = self._generate_suggestions(query, response)
            state["suggested_queries"] = suggestions
            
        except Exception as e:
            state["suggested_queries"] = []
        
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
        """Process a query through the entire workflow."""
        try:
            # Initialize state
            initial_state = AgentState(
                query=query,
                persona_type=persona_type,
                context="",
                documents=[],
                math_results={},
                sql_results={},
                final_response="",
                suggested_queries=[],
                error=None
            )
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
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
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "response": "Sorry, I encountered an error while processing your request."
            }

# Global agent router instance
agent_router = AgentRouter() 