from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from app.chatbot.database.database import ChatbotDatabase
from app.chatbot.database.vector_store import ChatbotVectorStore
from app.semantic_search.database.database import SemanticDatabase
from app.semantic_search.database.vector_store import SemanticVectorStore

router = APIRouter(prefix="/api", tags=["Documents"])

@router.get("/documents")
async def list_documents():
    """
    Get all uploaded documents metadata.
    """
    try:
        cb_db = ChatbotDatabase()
        documents = cb_db.get_all_documents()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all associated embeddings/chunks across BOTH Chatbot and Semantic Search systems.
    """
    cb_db = ChatbotDatabase()
    doc_info = cb_db.get_document_by_id(document_id)

    if not doc_info:
        raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found.")

    filepath_str = doc_info.get("filepath")

    try:
        # Delete from Chatbot DB & Vector Store
        cb_db.delete_document(document_id)
        ChatbotVectorStore().delete_document_chunks(document_id)

        # Delete from Semantic DB & Vector Store
        SemanticDatabase().delete_document(document_id)
        SemanticVectorStore().delete_document_chunks(document_id)

        # Remove physical file if it exists
        if filepath_str:
            file_path = Path(filepath_str)
            if file_path.exists():
                file_path.unlink(missing_ok=True)

        return {
            "message": f"Document '{doc_info.get('filename')}' (ID: {document_id}) deleted successfully from all systems.",
            "document_id": document_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
