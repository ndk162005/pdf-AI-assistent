from app.semantic_search.embeddings.embedding import SemanticEmbeddingModel

def test_semantic_embeddings_single():
    embedder = SemanticEmbeddingModel()
    vec = embedder.embed_text("Semantic search embedding query")
    assert isinstance(vec, list)
    assert len(vec) > 0

def test_semantic_embeddings_multiple():
    embedder = SemanticEmbeddingModel()
    vecs = embedder.embed_documents(["Passage 1", "Passage 2"])
    assert len(vecs) == 2
