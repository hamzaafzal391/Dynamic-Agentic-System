import os
import hashlib
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
    
    def add_document(self, content: str, metadata: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Add a document to the vector store."""
        try:
            if not self.text_splitter or not self.embeddings or not self.pinecone_index:
                return {"error": "Required dependencies not initialized"}
                
            if not doc_id:
                doc_id = hashlib.md5(content.encode()).hexdigest()
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Generate embeddings for chunks
            embeddings_list = self.embeddings.embed_documents(chunks)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                vector_id = f"{doc_id}_{i}"
                vector_data = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "doc_id": doc_id,
                        "content": chunk,
                        "chunk_size": len(chunk)
                    }
                }
                vectors.append(vector_data)
            
            # Upsert to Pinecone
            self.pinecone_index.upsert(vectors=vectors)
            return {
                "success": True,
                "doc_id": doc_id,
                "chunks_count": len(chunks),
                "content_length": len(content)
            }
        except Exception as e:
            return {"error": f"Failed to add document to vector store: {e}"}
    
    def search_documents(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for relevant documents using vector similarity."""
        try:
            if not self.embeddings or not self.pinecone_index:
                return {"error": "Required dependencies not initialized"}
                
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Pinecone
            search_kwargs = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filter_metadata:
                search_kwargs["filter"] = filter_metadata
            
            results = self.pinecone_index.query(**search_kwargs)
            
            # Process results
            documents = []
            if hasattr(results, 'matches'):
                for match in results.matches:
                    doc = {
                        "id": match.id,
                        "score": match.score,
                        "content": match.metadata.get("content", ""),
                        "metadata": {k: v for k, v in match.metadata.items() if k != "content"}
                    }
                    documents.append(doc)
            
            return {
                "success": True,
                "query": query,
                "documents": documents,
                "count": len(documents)
            }
            
        except Exception as e:
            return {"error": f"Failed to search documents: {e}"}
    
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