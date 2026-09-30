import uuid
import datetime
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
import config

# Chatbot imports
from app.chatbot.processing.pdf_extractor import ChatbotPDFExtractor, PDFExtractionError
from app.chatbot.processing.document_processor import ChatbotDocumentProcessor
from app.chatbot.embeddings.embedding import ChatbotEmbeddingModel
from app.chatbot.database.database import ChatbotDatabase
from app.chatbot.database.models import DocumentRecord as ChatbotDocRecord, ChunkRecord as ChatbotChunkRecord
from app.chatbot.database.vector_store import ChatbotVectorStore

# Semantic Search imports
from app.semantic_search.processing.pdf_extractor import SemanticPDFExtractor, SemanticPDFExtractionError
from app.semantic_search.processing.document_processor import SemanticDocumentProcessor
from app.semantic_search.embeddings.embedding import SemanticEmbeddingModel
from app.semantic_search.database.database import SemanticDatabase
from app.semantic_search.database.models import SemanticDocumentRecord, SemanticChunkRecord
from app.semantic_search.database.vector_store import SemanticVectorStore

router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF document through both Chatbot and Semantic Search pipelines independently.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save to disk safely
    safe_filename = Path(file.filename).name
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}_{safe_filename}"
    saved_path = config.UPLOAD_DIR / stored_filename

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file to filesystem: {str(e)}")

    # Verify magic bytes
    is_valid_pdf = False
    try:
        with open(saved_path, "rb") as f:
            header = f.read(4)
            if header == b"%PDF":
                is_valid_pdf = True
    except Exception as e:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to validate PDF content: {str(e)}")

    if not is_valid_pdf:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="File content is not a valid PDF document.")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # --- PIPELINE 1: CHATBOT INGESTION ---
    try:
        cb_extractor = ChatbotPDFExtractor(saved_path)
        cb_pages = cb_extractor.extract()
        cb_processor = ChatbotDocumentProcessor(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
        cb_chunks = cb_processor.process_document(doc_id=file_id, pages_data=cb_pages)

        cb_texts = [c["chunk_text"] for c in cb_chunks]
        cb_embedder = ChatbotEmbeddingModel()
        cb_embeddings = cb_embedder.embed_documents(cb_texts)

        cb_db = ChatbotDatabase()
        total_pages = cb_pages[0]["total_pages"] if cb_pages else 0
        cb_db.save_document(ChatbotDocRecord(
            document_id=file_id,
            filename=safe_filename,
            filepath=str(saved_path),
            total_pages=total_pages,
            created_at=now_iso
        ))
        cb_db.save_chunks([
            ChatbotChunkRecord(
                chunk_id=c["chunk_id"],
                document_id=c["doc_id"],
                filename=safe_filename,
                page_number=c["page_number"],
                chunk_text=c["chunk_text"]
            )
            for c in cb_chunks
        ])

        cb_vector_store = ChatbotVectorStore()
        cb_vector_store.add_chunks(chunks=cb_chunks, embeddings=cb_embeddings)

    except (PDFExtractionError, Exception) as e:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Chatbot pipeline processing error: {str(e)}")

    # --- PIPELINE 2: SEMANTIC SEARCH INGESTION ---
    try:
        sem_extractor = SemanticPDFExtractor(saved_path)
        sem_pages = sem_extractor.extract()
        sem_processor = SemanticDocumentProcessor(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
        sem_chunks = sem_processor.process_document(doc_id=file_id, pages_data=sem_pages)

        sem_texts = [c["chunk_text"] for c in sem_chunks]
        sem_embedder = SemanticEmbeddingModel()
        sem_embeddings = sem_embedder.embed_documents(sem_texts)

        sem_db = SemanticDatabase()
        sem_db.save_document(SemanticDocumentRecord(
            document_id=file_id,
            filename=safe_filename,
            filepath=str(saved_path),
            total_pages=total_pages,
            created_at=now_iso
        ))
        sem_db.save_chunks([
            SemanticChunkRecord(
                chunk_id=c["chunk_id"],
                document_id=c["doc_id"],
                filename=safe_filename,
                page_number=c["page_number"],
                chunk_text=c["chunk_text"]
            )
            for c in sem_chunks
        ])

        sem_vector_store = SemanticVectorStore()
        sem_vector_store.add_chunks(chunks=sem_chunks, embeddings=sem_embeddings)

    except (SemanticPDFExtractionError, Exception) as e:
        # Rollback chatbot database if semantic processing fails
        try:
            ChatbotDatabase().delete_document(file_id)
            ChatbotVectorStore().delete_document_chunks(file_id)
        except Exception:
            pass
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Semantic search pipeline processing error: {str(e)}")

    return {
        "message": "PDF uploaded and processed successfully across both independent intelligence systems.",
        "document_id": file_id,
        "filename": safe_filename,
        "total_pages": total_pages,
        "chatbot_chunks": len(cb_chunks),
        "semantic_chunks": len(sem_chunks)
    }
