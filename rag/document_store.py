import os
import hashlib
import uuid
from typing import List, Dict, Any, Optional
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    # Fallback for missing dependencies
    RecursiveCharacterTextSplitter = None
    OpenAIEmbeddings = None

from config import service_manager, Config

class DocumentStore:
    """Manages document storage and retrieval using Pinecone vector database."""
    
    def __init__(self):
        self.pinecone_index = service_manager.get_pinecone_index()
        
        if OpenAIEmbeddings:
            self.embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        else:
            self.embeddings = None
            
        if RecursiveCharacterTextSplitter:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
        else:
            self.text_splitter = None
    
    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are initialized."""
        return self.text_splitter is not None and self.embeddings is not None and self.pinecone_index is not None
    
    def _split_text(self, content: str) -> List[str]:
        """Split text into chunks using the text splitter."""
        if self.text_splitter:
            return self.text_splitter.split_text(content)
        else:
            # Fallback: simple split by sentences
            return [content]
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a document to the vector store."""
        if not self._check_dependencies():
            return {"success": False, "error": "Required dependencies not initialized"}
        
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            if metadata is None:
                metadata = {}
            metadata["doc_id"] = doc_id
            
            # Split content into chunks
            chunks = self._split_text(content)
            
            # Generate embeddings for chunks
            vectors = []
            for i, chunk in enumerate(chunks):
                embedding = self.embeddings.embed_query(chunk)
                vector_id = f"{doc_id}_chunk_{i}"
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {**metadata, "chunk_index": i, "content": chunk}
                })
            
            # Upsert to Pinecone
            self.pinecone_index.upsert(vectors=vectors)
            
            return {
                "success": True,
                "doc_id": doc_id,
                "chunks": len(chunks),
                "vectors": len(vectors)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_documents(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for documents using vector similarity."""
        if not self._check_dependencies():
            return {"success": False, "error": "Required dependencies not initialized"}
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Prepare search parameters
            search_kwargs = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filter_metadata:
                search_kwargs["filter"] = filter_metadata
            
            # Search Pinecone
            results = self.pinecone_index.query(**search_kwargs)
            
            # Process results
            documents = []
            if hasattr(results, 'matches'):
                for i, match in enumerate(results.matches):
                    if match.metadata and "content" in match.metadata:
                        doc = {
                            "id": match.id,
                            "content": match.metadata["content"],
                            "score": match.score,
                            "metadata": {k: v for k, v in match.metadata.items() if k != "content"}
                        }
                        documents.append(doc)
            
            return {
                "success": True,
                "documents": documents,
                "query": query,
                "top_k": top_k
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        try:
            results = self.pinecone_index.query(
                vector=[0] * 1536,  # Dummy vector for metadata-only query
                top_k=1000,
                include_metadata=True,
                filter={"doc_id": doc_id}
            )
            
            chunks = []
            for match in results.matches:
                chunk = {
                    "id": match.id,
                    "content": match.metadata.get("content", ""),
                    "chunk_index": match.metadata.get("chunk_index", 0),
                    "metadata": {k: v for k, v in match.metadata.items() if k not in ["content", "chunk_index"]}
                }
                chunks.append(chunk)
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x["chunk_index"])
            return chunks
            
        except Exception as e:
            raise Exception(f"Failed to get document chunks: {e}")
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete all chunks for a specific document."""
        try:
            # Get all chunk IDs for the document
            chunks = self.get_document_chunks(doc_id)
            chunk_ids = [chunk["id"] for chunk in chunks]
            
            if chunk_ids:
                self.pinecone_index.delete(ids=chunk_ids)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to delete document: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the document store."""
        try:
            stats = self.pinecone_index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}

# Global document store instance
document_store = DocumentStore() 