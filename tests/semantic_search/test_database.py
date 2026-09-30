import datetime
from app.semantic_search.database.database import SemanticDatabase
from app.semantic_search.database.models import SemanticDocumentRecord, SemanticChunkRecord
from app.semantic_search.database.vector_store import SemanticVectorStore

def test_semantic_sqlite_database(tmp_path):
    db_path = tmp_path / "semantic.db"
    db = SemanticDatabase(db_path=db_path)

    doc_rec = SemanticDocumentRecord(
        document_id="s1",
        filename="guide.pdf",
        filepath=str(tmp_path / "guide.pdf"),
        total_pages=3,
        created_at=datetime.datetime.utcnow().isoformat()
    )
    db.save_document(doc_rec)
    db.save_chunks([
        SemanticChunkRecord(chunk_id="sc1", document_id="s1", filename="guide.pdf", page_number=1, chunk_text="Chunk 1")
    ])

    docs = db.get_all_documents()
    assert len(docs) == 1
    assert docs[0]["filename"] == "guide.pdf"

    db.delete_document("s1")
    assert len(db.get_all_documents()) == 0

def test_semantic_vector_store(tmp_path):
    vdb_path = tmp_path / "sem_vdb"
    vstore = SemanticVectorStore(vector_db_path=vdb_path)

    chunks = [
        {"chunk_id": "sc1", "doc_id": "s1", "filename": "guide.pdf", "page_number": 1, "chunk_text": "Semantic snippet"}
    ]
    embeddings = [[0.02] * 384]

    vstore.add_chunks(chunks, embeddings)
    res = vstore.query(query_embedding=[0.02] * 384, top_k=1)
    assert len(res) == 1
    assert res[0]["chunk_id"] == "sc1"
