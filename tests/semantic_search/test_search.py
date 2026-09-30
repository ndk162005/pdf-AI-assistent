from app.semantic_search.search.semantic_search import SemanticSearchEngine
from app.semantic_search.database.vector_store import SemanticVectorStore

def test_semantic_search_engine_empty_query():
    engine = SemanticSearchEngine()
    results = engine.search("")
    assert results == []
