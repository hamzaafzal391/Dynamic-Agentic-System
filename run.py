#!/usr/bin/env python3
"""
Startup script for the Dynamic Agentic System.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the application."""
    try:
        # Import and run the FastAPI application
        from api.main import app
        import uvicorn
        from config import Config
        
        print("🚀 Starting Dynamic Agentic System...")
        print(f"📡 Server will be available at http://{Config.HOST}:{Config.PORT}")
        print(f"📚 API documentation at http://{Config.HOST}:{Config.PORT}/docs")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(
            "api.main:app",
            host=Config.HOST,
            port=Config.PORT,
            reload=Config.DEBUG,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 