#!/usr/bin/env python3
"""
Test script for PDF upload functionality.
"""

import requests
import os
from pathlib import Path

def test_pdf_upload():
    """Test PDF upload to the API."""
    
    # API endpoint
    url = "http://localhost:8000/upload"
    
    # Create a simple test PDF or use an existing one
    test_pdf_path = "./data/docs/test.pdf"
    
    # Check if test PDF exists, if not create a simple one
    if not os.path.exists(test_pdf_path):
        print("Creating test PDF...")
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(test_pdf_path, pagesize=letter)
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 700, "This is a test PDF for upload functionality.")
            c.drawString(100, 650, "It contains some sample text to test OCR and text extraction.")
            c.save()
            print(f"Created test PDF: {test_pdf_path}")
        except ImportError:
            print("reportlab not available, skipping PDF creation")
            return
    
    # Test the upload
    try:
        with open(test_pdf_path, 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            
            print(f"Uploading {test_pdf_path} to {url}...")
            response = requests.post(url, files=files)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Upload successful!")
                    print(f"Message: {result.get('message')}")
                    print(f"File ID: {result.get('file_id')}")
                    print(f"File Path: {result.get('file_path')}")
                else:
                    print("❌ Upload failed!")
                    print(f"Error: {result.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Exception during upload: {e}")

def test_api_status():
    """Test API status endpoint."""
    try:
        response = requests.get("http://localhost:8000/status")
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"System Status: {status.get('status')}")
            print(f"Services: {status.get('services')}")
    except Exception as e:
        print(f"❌ API Status check failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing PDF Upload Functionality")
    print("=" * 50)
    
    # Test API status first
    test_api_status()
    print()
    
    # Test PDF upload
    test_pdf_upload() 