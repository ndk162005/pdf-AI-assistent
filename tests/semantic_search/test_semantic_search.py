from app.semantic_search.database.database import SemanticDatabase
from app.semantic_search.database.vector_store import SemanticVectorStore
from app.semantic_search.search.semantic_search import SemanticSearchEngine
from app.semantic_search.search.ranking import ResultRanker

def test_complete_semantic_search_flow(tmp_path):
    db_path = tmp_path / "sem.db"
    vdb_path = tmp_path / "sem_vdb"

    db = SemanticDatabase(db_path=db_path)
    vstore = SemanticVectorStore(vector_db_path=vdb_path)

    # Ingest mock semantic chunks
    chunk_data = [
        {"chunk_id": "sc1", "doc_id": "sd1", "filename": "policy.pdf", "page_number": 5, "chunk_text": "Port safety regulations policy statement."}
    ]
    vstore.add_chunks(chunk_data, [[0.01] * 384])

    engine = SemanticSearchEngine(vector_store=vstore)
    raw_matches = engine.search("safety regulations", top_k=1)
    ranked = ResultRanker.rank_results(raw_matches)

    assert len(ranked) == 1
    assert ranked[0]["rank"] == 1
    assert ranked[0]["document"] == "policy.pdf"
    assert ranked[0]["page"] == 5
    assert "safety regulations" in ranked[0]["text"]
