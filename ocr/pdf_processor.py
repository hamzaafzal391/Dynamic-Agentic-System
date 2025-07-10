try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("⚠️  pdfplumber not available. PDF processing will be limited.")
import pytesseract
from PIL import Image
import io
import os
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from datetime import datetime
from config import Config

class PDFProcessor:
    """Handles PDF processing, text extraction, and OCR using PyMuPDF and Tesseract."""
    
    def __init__(self):
        self.upload_dir = Config.UPLOAD_DIR
        self.max_file_size = Config.MAX_FILE_SIZE
        
        # Configure Tesseract path if provided
        if Config.TESSERACT_CMD_PATH:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD_PATH
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF using pdfplumber."""
        if not PDFPLUMBER_AVAILABLE:
            return {"error": "pdfplumber not available. Please install pdfplumber for PDF processing."}
            
        try:
            if not os.path.exists(pdf_path):
                return {"error": f"PDF file not found: {pdf_path}"}
            
            # Check file size
            file_size = os.path.getsize(pdf_path)
            if file_size > self.max_file_size:
                return {"error": f"File size {file_size} exceeds maximum allowed size {self.max_file_size}"}
            
            text_content = []
            page_images = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text() or ""
                    text_content.append({
                        "page": page_num + 1,
                        "text": text,
                        "text_length": len(text)
                    })
                    
                    # Extract page as image for OCR
                    try:
                        img = page.to_image()
                        img_data = img.original.convert('RGB')
                        
                        # Convert to bytes for storage
                        img_bytes = io.BytesIO()
                        img_data.save(img_bytes, format='PNG')
                        img_data_bytes = img_bytes.getvalue()
                        
                        # Perform OCR
                        ocr_text = pytesseract.image_to_string(img_data)
                        
                        page_images.append({
                            "page": page_num + 1,
                            "image_data": img_data_bytes,
                            "ocr_text": ocr_text,
                            "ocr_text_length": len(ocr_text)
                        })
                    except Exception as img_error:
                        # If image extraction fails, continue with text only
                        page_images.append({
                            "page": page_num + 1,
                            "image_data": None,
                            "ocr_text": "",
                            "ocr_text_length": 0,
                            "error": str(img_error)
                        })
            
            return {
                "success": True,
                "file_path": pdf_path,
                "total_pages": len(text_content),
                "text_content": text_content,
                "page_images": page_images,
                "file_size": file_size,
                "extraction_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to extract text from PDF: {str(e)}"}
    
    def extract_images_from_pdf(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Extract images from PDF pages."""
        if not PDFPLUMBER_AVAILABLE:
            return {"error": "pdfplumber not available. Please install pdfplumber for PDF processing."}
            
        try:
            if not os.path.exists(pdf_path):
                return {"error": f"PDF file not found: {pdf_path}"}
            
            if not output_dir:
                output_dir = os.path.join(self.upload_dir, "extracted_images")
            
            os.makedirs(output_dir, exist_ok=True)
            
            extracted_images = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract images from page
                    images = page.images
                    
                    for img_index, img in enumerate(images):
                        try:
                            # Get image data
                            img_data = img['stream'].get_data()
                            
                            # Generate filename
                            image_filename = f"page_{page_num + 1}_image_{img_index + 1}.png"
                            image_path = os.path.join(output_dir, image_filename)
                            
                            # Save image
                            with open(image_path, "wb") as img_file:
                                img_file.write(img_data)
                            
                            extracted_images.append({
                                "page": page_num + 1,
                                "image_index": img_index + 1,
                                "filename": image_filename,
                                "file_path": image_path,
                                "size": len(img_data),
                                "format": "png"
                            })
                        except Exception as img_error:
                            # Skip images that can't be extracted
                            continue
            
            return {
                "success": True,
                "extracted_images": extracted_images,
                "total_images": len(extracted_images),
                "output_dir": output_dir
            }
            
        except Exception as e:
            return {"error": f"Failed to extract images from PDF: {str(e)}"}
    
    def perform_ocr_on_image(self, image_path: str) -> Dict[str, Any]:
        """Perform OCR on a single image."""
        try:
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
            
            # Open image
            img = Image.open(image_path)
            
            # Perform OCR
            ocr_text = pytesseract.image_to_string(img)
            
            # Get image information
            img_info = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
            
            return {
                "success": True,
                "image_path": image_path,
                "ocr_text": ocr_text,
                "text_length": len(ocr_text),
                "image_info": img_info
            }
            
        except Exception as e:
            return {"error": f"Failed to perform OCR on image: {str(e)}"}
    
    def process_pdf_with_ocr(self, pdf_path: str, save_images: bool = False) -> Dict[str, Any]:
        """Process PDF with both text extraction and OCR."""
        try:
            # Extract text first
            text_result = self.extract_text_from_pdf(pdf_path)
            
            if not text_result.get("success"):
                return text_result
            
            # Extract images if requested
            images_result = None
            if save_images:
                images_result = self.extract_images_from_pdf(pdf_path)
            
            # Combine results
            result = {
                "success": True,
                "file_path": pdf_path,
                "total_pages": text_result["total_pages"],
                "text_extraction": text_result,
                "images_extraction": images_result,
                "processing_time": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to process PDF: {str(e)}"}
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        if not PDFPLUMBER_AVAILABLE:
            return {"error": "pdfplumber not available. Please install pdfplumber for PDF processing."}
            
        try:
            if not os.path.exists(pdf_path):
                return {"error": f"PDF file not found: {pdf_path}"}
            
            with pdfplumber.open(pdf_path) as pdf:
                metadata = {
                    "file_path": pdf_path,
                    "file_size": os.path.getsize(pdf_path),
                    "total_pages": len(pdf.pages),
                    "pdf_metadata": pdf.metadata,
                    "page_dimensions": []
                }
                
                # Get page dimensions
                for page_num, page in enumerate(pdf.pages):
                    width = page.width
                    height = page.height
                    metadata["page_dimensions"].append({
                        "page": page_num + 1,
                        "width": width,
                        "height": height
                    })
                
                return {
                    "success": True,
                    "metadata": metadata
                }
            
        except Exception as e:
            return {"error": f"Failed to extract PDF metadata: {str(e)}"}
    
    def save_uploaded_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Save uploaded PDF file to the upload directory."""
        try:
            # Create upload directory if it doesn't exist
            os.makedirs(self.upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_hash = hashlib.md5(file_content).hexdigest()
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{file_hash}{file_ext}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Get file metadata
            file_size = len(file_content)
            
            return {
                "success": True,
                "original_filename": filename,
                "saved_filename": unique_filename,
                "file_path": file_path,
                "file_size": file_size,
                "upload_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to save uploaded PDF: {str(e)}"}

# Global PDF processor instance
pdf_processor = PDFProcessor() 