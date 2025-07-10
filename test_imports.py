#!/usr/bin/env python3
"""
Test script to identify which import is causing DLL issues.
"""

def test_imports():
    """Test imports one by one to identify the problematic package."""
    
    print("Testing imports...")
    
    try:
        print("✓ Testing basic imports...")
        import os
        import sys
        import json
        print("✓ Basic imports successful")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return
    
    try:
        print("✓ Testing FastAPI...")
        import fastapi
        print("✓ FastAPI successful")
    except Exception as e:
        print(f"❌ FastAPI failed: {e}")
        return
    
    try:
        print("✓ Testing pandas...")
        import pandas as pd
        print("✓ Pandas successful")
    except Exception as e:
        print(f"❌ Pandas failed: {e}")
        return
    
    try:
        print("✓ Testing numpy...")
        import numpy as np
        print("✓ NumPy successful")
    except Exception as e:
        print(f"❌ NumPy failed: {e}")
        return
    
    try:
        print("✓ Testing openai...")
        import openai
        print("✓ OpenAI successful")
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return
    
    try:
        print("✓ Testing pinecone...")
        from pinecone import Pinecone
        print("✓ Pinecone successful")
    except Exception as e:
        print(f"❌ Pinecone failed: {e}")
        return
    
    try:
        print("✓ Testing langchain...")
        import langchain
        print("✓ LangChain successful")
    except Exception as e:
        print(f"❌ LangChain failed: {e}")
        return
    
    try:
        print("✓ Testing langgraph...")
        import langgraph
        print("✓ LangGraph successful")
    except Exception as e:
        print(f"❌ LangGraph failed: {e}")
        return
    
    try:
        print("✓ Testing pymupdf...")
        import fitz
        print("✓ PyMuPDF successful")
    except Exception as e:
        print(f"❌ PyMuPDF failed: {e}")
        return
    
    try:
        print("✓ Testing pytesseract...")
        import pytesseract
        print("✓ PyTesseract successful")
    except Exception as e:
        print(f"❌ PyTesseract failed: {e}")
        return
    
    print("🎉 All imports successful!")

if __name__ == "__main__":
    test_imports() 