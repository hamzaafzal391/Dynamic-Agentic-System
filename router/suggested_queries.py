from typing import List, Dict, Any, Optional
from config import service_manager

class SuggestedQueriesGenerator:
    """Generates suggested follow-up queries based on the current query and response."""
    
    def __init__(self):
        self.openai_client = service_manager.get_openai_client()
    
    def generate_suggestions(self, query: str, response: str, context: str = "", max_suggestions: int = 3) -> List[str]:
        """Generate suggested follow-up queries using OpenAI."""
        try:
            if not self.openai_client:
                return self._generate_fallback_suggestions(query, response, max_suggestions)
            
            prompt = f"""
            Based on the following query and response, generate {max_suggestions} relevant follow-up questions that would be helpful for the user.
            
            Original Query: {query}
            Response: {response}
            Context: {context}
            
            The suggestions should be:
            1. Relevant to the original query
            2. Helpful for gaining more information
            3. Natural and conversational
            4. Different from each other
            
            Return only the questions, one per line, without numbering or bullet points.
            """
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that generates relevant follow-up questions."},
                {"role": "user", "content": prompt}
            ]
            
            response_obj = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            suggestions_text = response_obj.choices[0].message.content
            if suggestions_text:
                suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
                return suggestions[:max_suggestions]
            
            return self._generate_fallback_suggestions(query, response, max_suggestions)
            
        except Exception as e:
            return self._generate_fallback_suggestions(query, response, max_suggestions)
    
    def _generate_fallback_suggestions(self, query: str, response: str, max_suggestions: int = 3) -> List[str]:
        """Generate fallback suggestions using rule-based approach."""
        suggestions = []
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Document-related suggestions
        if any(word in query_lower for word in ["document", "pdf", "file", "text", "content"]):
            suggestions.extend([
                "Can you search for more specific information in the documents?",
                "What are the key findings from the uploaded documents?",
                "Can you summarize the main points from the documents?",
                "Are there any important dates or figures mentioned in the documents?",
                "What conclusions can be drawn from the document analysis?"
            ])
        
        # Math-related suggestions
        if any(word in query_lower for word in ["calculate", "compute", "math", "statistics", "average", "sum", "percentage"]):
            suggestions.extend([
                "Can you perform additional calculations on this data?",
                "What statistical analysis can be done on these numbers?",
                "Can you create a visualization of these results?",
                "What are the trends in this data?",
                "Can you compare these results with historical data?"
            ])
        
        # Database-related suggestions
        if any(word in query_lower for word in ["database", "table", "sql", "query", "data", "records"]):
            suggestions.extend([
                "What other tables are available in the database?",
                "Can you show me the structure of the tables?",
                "What queries can I run on this data?",
                "Are there any relationships between the tables?",
                "Can you provide more detailed analysis of this data?"
            ])
        
        # Financial-related suggestions
        if any(word in query_lower for word in ["stock", "price", "market", "investment", "financial", "revenue", "profit"]):
            suggestions.extend([
                "What are the recent trends in this stock?",
                "How does this compare to competitors?",
                "What factors might affect this investment?",
                "Can you provide a risk analysis?",
                "What are the growth projections?"
            ])
        
        # Legal-related suggestions
        if any(word in query_lower for word in ["legal", "law", "contract", "regulation", "compliance", "liability"]):
            suggestions.extend([
                "What are the legal implications of this?",
                "Are there any compliance requirements?",
                "What are the potential risks involved?",
                "How does this relate to current regulations?",
                "What documentation would be needed?"
            ])
        
        # General suggestions
        general_suggestions = [
            "Can you provide more details about this?",
            "What are the implications of this information?",
            "How does this relate to other data we have?",
            "What are the next steps based on this analysis?",
            "Are there any recommendations you can make?"
        ]
        
        # Add general suggestions if we don't have enough specific ones
        suggestions.extend(general_suggestions)
        
        # Remove duplicates and limit to max_suggestions
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
            if len(unique_suggestions) >= max_suggestions:
                break
        
        return unique_suggestions[:max_suggestions]
    
    def generate_contextual_suggestions(self, query: str, documents: List[Dict[str, Any]], 
                                      math_results: Dict[str, Any], sql_results: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on available data and results."""
        suggestions = []
        
        # Document-based suggestions
        if documents:
            doc_count = len(documents)
            suggestions.append(f"Can you analyze the {doc_count} relevant documents in more detail?")
            suggestions.append("What are the key insights from the document search?")
        
        # Math-based suggestions
        if math_results:
            suggestions.append("Can you perform additional mathematical analysis?")
            suggestions.append("What statistical insights can be derived from these calculations?")
        
        # SQL-based suggestions
        if sql_results:
            if "available_tables" in sql_results:
                table_count = len(sql_results["available_tables"])
                suggestions.append(f"Can you explore the {table_count} available database tables?")
            suggestions.append("What additional database queries would be helpful?")
        
        # Mixed suggestions
        if documents and (math_results or sql_results):
            suggestions.append("How do the documents relate to the numerical data?")
            suggestions.append("Can you cross-reference the document findings with the database?")
        
        return suggestions[:3]
    
    def generate_persona_specific_suggestions(self, query: str, persona_type: str) -> List[str]:
        """Generate suggestions specific to the persona type."""
        suggestions = []
        
        if persona_type == "financial":
            suggestions.extend([
                "What are the investment implications of this analysis?",
                "How does this affect portfolio strategy?",
                "What are the risk factors to consider?",
                "Can you provide market trend analysis?",
                "What are the financial projections?"
            ])
        
        elif persona_type == "legal":
            suggestions.extend([
                "What are the legal implications of this information?",
                "Are there any compliance considerations?",
                "What documentation would be required?",
                "What are the potential legal risks?",
                "How does this relate to current regulations?"
            ])
        
        elif persona_type == "general":
            suggestions.extend([
                "Can you provide more context about this topic?",
                "What are the broader implications?",
                "How does this relate to current trends?",
                "What are the key takeaways?",
                "What additional research would be helpful?"
            ])
        
        return suggestions[:3]

# Global suggested queries generator instance
suggested_queries_generator = SuggestedQueriesGenerator()

def get_suggested_queries() -> List[str]:
    """Get general suggested queries for the system."""
    return [
        "What is 25 * 4 + 10?",
        "Show me stock data for AAPL",
        "Calculate moving average for GOOGL",
        "What are the statistics for MSFT?",
        "Search for documents about artificial intelligence",
        "How does machine learning work?",
        "What are the latest trends in technology?",
        "Can you help me with financial analysis?",
        "What legal documents should I review?",
        "Tell me about data science"
    ] 