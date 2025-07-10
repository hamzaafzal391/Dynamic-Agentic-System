from typing import Dict, Any, List, Optional
from enum import Enum
from openai.types.chat import ChatCompletionMessageParam
from config import service_manager

class PersonaType(Enum):
    FINANCIAL = "financial"
    LEGAL = "legal"
    GENERAL = "general"

class Persona:
    """Base persona class for different agent types."""
    
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.openai_client = service_manager.get_openai_client()
    
    def get_response(self, query: str, context: str = "") -> str:
        """Get response from the persona."""
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuery: {query}"}
        ]
        
        try:
            if self.openai_client is None:
                return "Error: OpenAI client not initialized"
                
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content if content else "No response generated"
        except Exception as e:
            return f"Error generating response: {e}"

class FinancialPersona(Persona):
    """Financial advisor persona specialized in financial analysis and advice."""
    
    def __init__(self):
        system_prompt = """You are a professional financial advisor with expertise in:
        - Stock market analysis and investment strategies
        - Financial planning and portfolio management
        - Economic trends and market indicators
        - Risk assessment and mitigation
        - Regulatory compliance and financial regulations
        
        Provide clear, actionable financial advice with appropriate disclaimers.
        Always consider risk factors and recommend consulting with licensed professionals for specific investment decisions.
        Use data-driven analysis when available and cite sources when possible."""
        
        super().__init__(
            name="Financial Advisor",
            description="Expert in financial analysis, investment strategies, and market trends",
            system_prompt=system_prompt
        )

class LegalPersona(Persona):
    """Legal advisor persona specialized in legal analysis and guidance."""
    
    def __init__(self):
        system_prompt = """You are a legal advisor with expertise in:
        - Contract law and legal document analysis
        - Corporate law and business regulations
        - Intellectual property and compliance
        - Risk assessment and legal implications
        - Regulatory frameworks and legal precedents
        
        Provide general legal information and guidance, but always recommend consulting with qualified legal professionals for specific legal matters.
        Clarify that you are not providing legal advice and that users should seek professional legal counsel for their specific situations."""
        
        super().__init__(
            name="Legal Advisor",
            description="Expert in legal analysis, compliance, and regulatory guidance",
            system_prompt=system_prompt
        )

class GeneralPersona(Persona):
    """General assistant persona for broad knowledge and assistance."""
    
    def __init__(self):
        system_prompt = """You are a knowledgeable general assistant with broad expertise in:
        - General knowledge and research
        - Problem-solving and analysis
        - Writing and communication
        - Technology and tools
        - Best practices and recommendations
        
        Provide helpful, accurate, and well-reasoned responses to a wide variety of questions.
        Be conversational yet professional, and always aim to be helpful and informative."""
        
        super().__init__(
            name="General Assistant",
            description="Versatile assistant for general knowledge and problem-solving",
            system_prompt=system_prompt
        )

class PersonaManager:
    """Manages different personas and their selection."""
    
    def __init__(self):
        self.personas = {
            PersonaType.FINANCIAL: FinancialPersona(),
            PersonaType.LEGAL: LegalPersona(),
            PersonaType.GENERAL: GeneralPersona()
        }
    
    def get_persona(self, persona_type: PersonaType) -> Persona:
        """Get a specific persona by type."""
        return self.personas.get(persona_type, self.personas[PersonaType.GENERAL])
    
    def get_available_personas(self) -> List[Dict[str, Any]]:
        """Get list of available personas with their descriptions."""
        return [
            {
                "type": persona_type.value,
                "name": persona.name,
                "description": persona.description
            }
            for persona_type, persona in self.personas.items()
        ]
    
    def route_query(self, query: str, persona_type: PersonaType, context: str = "") -> str:
        """Route a query to the appropriate persona."""
        persona = self.get_persona(persona_type)
        return persona.get_response(query, context)

# Global persona manager instance
persona_manager = PersonaManager() 