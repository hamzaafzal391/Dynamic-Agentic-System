import os
from dotenv import load_dotenv
from typing import Optional
from pinecone import Pinecone
from openai import OpenAI

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the dynamic agentic system."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4"
    
    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "dynamic-agentic-system")
    
    # Data Configuration
    STOCK_DATA_DIR: str = os.getenv("STOCK_DATA_DIR", "./data/stocks")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # OCR Configuration
    TESSERACT_CMD_PATH: str = os.getenv("TESSERACT_CMD_PATH", "/usr/bin/tesseract")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/docs")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = [
            "OPENAI_API_KEY",
            "PINECONE_API_KEY", 
            "PINECONE_ENVIRONMENT"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True

class ServiceManager:
    """Manages initialization of external services."""
    
    def __init__(self):
        self.pinecone_index = None
        self.openai_client = None
    
    def initialize_pinecone(self) -> bool:
        """Initialize Pinecone client and index."""
        try:
            pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in pc.list_indexes()]
            if Config.PINECONE_INDEX_NAME not in existing_indexes:
                pc.create_index(
                    name=Config.PINECONE_INDEX_NAME,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine",
                    spec=pc.ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.pinecone_index = pc.Index(Config.PINECONE_INDEX_NAME)
            return True
            
        except Exception as e:
            print(f"Failed to initialize Pinecone: {e}")
            return False
    
    def initialize_openai(self) -> bool:
        """Initialize OpenAI client."""
        try:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            return True
            
        except Exception as e:
            print(f"Failed to initialize OpenAI: {e}")
            return False
    
    def get_pinecone_index(self):
        """Get Pinecone index instance."""
        if not self.pinecone_index:
            self.initialize_pinecone()
        return self.pinecone_index
    
    def get_openai_client(self):
        """Get OpenAI client instance."""
        if not self.openai_client:
            self.initialize_openai()
        return self.openai_client

# Global service manager instance
service_manager = ServiceManager() 