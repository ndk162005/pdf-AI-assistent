import pytest
import datetime
from app.chatbot.database.database import ChatbotDatabase
from app.chatbot.database.models import DocumentRecord, ChunkRecord
from app.chatbot.database.vector_store import ChatbotVectorStore

def test_chatbot_sqlite_database(tmp_path):
    db_path = tmp_path / "test_chatbot.db"
    db = ChatbotDatabase(db_path=db_path)
    
    doc_rec = DocumentRecord(
        document_id="doc_1",
        filename="test.pdf",
        filepath=str(tmp_path / "test.pdf"),
        total_pages=5,
        created_at=datetime.datetime.utcnow().isoformat()
    )
    db.save_document(doc_rec)
    
    chunks = [
        ChunkRecord(chunk_id="c1", document_id="doc_1", filename="test.pdf", page_number=1, chunk_text="Text 1"),
        ChunkRecord(chunk_id="c2", document_id="doc_1", filename="test.pdf", page_number=2, chunk_text="Text 2")
    ]
    db.save_chunks(chunks)

    docs = db.get_all_documents()
    assert len(docs) == 1
    assert docs[0]["filename"] == "test.pdf"

    db.delete_document("doc_1")
    assert len(db.get_all_documents()) == 0

def test_chatbot_vector_store(tmp_path):
    vdb_path = tmp_path / "vector_db"
    vstore = ChatbotVectorStore(vector_db_path=vdb_path)

    chunks = [
        {"chunk_id": "c1", "doc_id": "d1", "filename": "test.pdf", "page_number": 1, "chunk_text": "Sample vector text"}
    ]
    embeddings = [[0.1] * 384]

    vstore.add_chunks(chunks, embeddings)
    res = vstore.query(query_embedding=[0.1] * 384, top_k=1)
    assert len(res) == 1
    assert res[0]["chunk_id"] == "c1"

    vstore.delete_document_chunks("d1")
