from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime

# Import our modules
from config import Config, service_manager
from agents.personas import PersonaType, persona_manager
from router.agent_router import agent_router
from router.suggested_queries import suggested_queries_generator
from rag.document_store import document_store
from ocr.pdf_processor import pdf_processor

# Initialize FastAPI app
app = FastAPI(
    title="Dynamic Agentic System",
    description="A multi-agent system for document processing, math computation, and database querying",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    persona_type: Optional[str] = "general"
    context: Optional[str] = ""

class QueryResponse(BaseModel):
    success: bool
    response: str
    suggested_queries: List[str]
    documents: List[Dict[str, Any]]
    math_results: Dict[str, Any]
    sql_results: Dict[str, Any]
    error: Optional[str] = None
    processing_time: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    services: Dict[str, bool]
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("Initializing Dynamic Agentic System...")
    
    # Validate configuration
    if not Config.validate():
        print("Warning: Some required environment variables are missing.")
    
    # Initialize services
    try:
        service_manager.initialize_pinecone()
        service_manager.initialize_openai()
        print("Services initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize some services: {e}")

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Dynamic Agentic System API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/query - Process queries with multi-agent system",
            "upload": "/upload - Upload PDF documents",
            "personas": "/personas - Get available personas",
            "status": "/status - System status and health check"
        }
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    print("[DEBUG] API received request:", request.dict())
    start_time = datetime.now()
    
    try:
        # Validate persona type
        try:
            persona_type_str = request.persona_type or "general"
            persona_type = PersonaType(persona_type_str.lower())
        except ValueError:
            persona_type = PersonaType.GENERAL
        
        # Process query through agent router
        result = agent_router.process_query(
            query=request.query,
            persona_type=persona_type
        )
        
        # Add processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        response_obj = QueryResponse(
            success=result["success"],
            response=result["response"],
            suggested_queries=result.get("suggested_queries", []),
            documents=result.get("documents", []),
            math_results=result.get("math_results", {}),
            sql_results=result.get("sql_results", {}),
            error=result.get("error"),
            processing_time=f"{processing_time:.2f}s"
        )
        print("[DEBUG] API SENDING RESPONSE:", response_obj.dict())
        return response_obj
        
    except Exception as e:
        return QueryResponse(
            success=False,
            response="An error occurred while processing your query.",
            suggested_queries=[],
            documents=[],
            math_results={},
            sql_results={},
            error=str(e),
            processing_time=f"{(datetime.now() - start_time).total_seconds():.2f}s"
        )

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document."""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File size exceeds maximum allowed size of {Config.MAX_FILE_SIZE} bytes"
            )
        
        # Save uploaded file
        save_result = pdf_processor.save_uploaded_pdf(content, file.filename)
        
        if not save_result.get("success"):
            raise HTTPException(status_code=500, detail=save_result.get("error", "Failed to save file"))
        
        # Process PDF with OCR
        process_result = pdf_processor.process_pdf_with_ocr(
            save_result["file_path"], 
            save_images=False
        )
        
        if not process_result.get("success"):
            raise HTTPException(status_code=500, detail=process_result.get("error", "Failed to process PDF"))
        
        # Extract text content for vector store
        text_content = process_result["text_extraction"]["text_content"]
        all_text = "\n\n".join([page["text"] for page in text_content])
        
        # Add to document store
        metadata = {
            "filename": save_result["original_filename"],
            "file_path": save_result["file_path"],
            "file_size": save_result["file_size"],
            "upload_time": save_result["upload_time"],
            "total_pages": process_result["total_pages"],
            "file_type": "pdf"
        }
        
        doc_result = document_store.add_document(all_text, metadata)
        print("[DEBUG] add_document result:", doc_result)
        
        if not doc_result.get("success"):
            raise HTTPException(status_code=500, detail=doc_result.get("error", "Failed to add document to vector store"))
        
        doc_id = doc_result.get("doc_id")
        
        return UploadResponse(
            success=True,
            message=f"PDF uploaded and processed successfully. {process_result['total_pages']} pages extracted.",
            file_id=doc_id,
            file_path=save_result["file_path"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return UploadResponse(
            success=False,
            message="Failed to upload and process PDF",
            error=str(e)
        )

@app.get("/personas")
async def get_personas():
    """Get available personas."""
    try:
        personas = persona_manager.get_available_personas()
        return {
            "success": True,
            "personas": personas,
            "count": len(personas)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "personas": []
        }

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status and health check."""
    try:
        services = {
            "openai": service_manager.openai_client is not None,
            "pinecone": service_manager.pinecone_index is not None,
            "document_store": document_store is not None,
            "pdf_processor": pdf_processor is not None,
            "agent_router": agent_router is not None
        }
        
        # Check if all critical services are available
        all_services_ok = all(services.values())
        
        return SystemStatus(
            status="healthy" if all_services_ok else "degraded",
            services=services,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        return SystemStatus(
            status="error",
            services={},
            timestamp=datetime.now().isoformat()
        )

@app.get("/documents/stats")
async def get_document_stats():
    """Get document store statistics."""
    try:
        stats = document_store.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/datasets")
async def get_datasets():
    """Get available CSV datasets and PDF documents."""
    try:
        from math_ops.data_processor import data_processor
        from ocr.pdf_processor import pdf_processor
        import os
        
        # Get CSV datasets
        csv_result = data_processor.get_available_datasets()
        
        # Get PDF documents
        pdf_datasets = []
        if os.path.exists(Config.UPLOAD_DIR):
            for file in os.listdir(Config.UPLOAD_DIR):
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(Config.UPLOAD_DIR, file)
                    file_size = os.path.getsize(file_path)
                    # Try to read metadata JSON
                    meta_path = file_path + ".meta.json"
                    original_filename = file.replace('.pdf', '')
                    if os.path.exists(meta_path):
                        import json
                        try:
                            with open(meta_path, "r", encoding="utf-8") as mf:
                                meta = json.load(mf)
                                original_filename = meta.get("original_filename", original_filename)
                        except Exception:
                            pass
                    pdf_datasets.append({
                        'name': original_filename,
                        'file_path': file_path,
                        'file_type': 'pdf',
                        'file_size': file_size,
                        'rows': 1,  # PDFs don't have rows like CSVs
                        'columns': ['content', 'pages', 'metadata']
                    })
        
        # Combine results
        all_datasets = []
        if csv_result.get("success"):
            all_datasets.extend(csv_result["datasets"])
        all_datasets.extend(pdf_datasets)
        
        return {
            "success": True,
            "datasets": all_datasets,
            "count": len(all_datasets),
            "csv_count": len(csv_result.get("datasets", [])),
            "pdf_count": len(pdf_datasets)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/suggested-queries")
async def get_suggested_queries():
    """Get suggested follow-up queries."""
    try:
        from router.suggested_queries import get_suggested_queries
        suggestions = get_suggested_queries()
        return {
            "success": True,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestions": []
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    ) 