from typing import List, Dict, Any
from app.semantic_search.embeddings.embedding import SemanticEmbeddingModel
from app.semantic_search.database.vector_store import SemanticVectorStore
import config

class SemanticSearchEngine:
    """Semantic Search Engine module for vector query matching."""

    def __init__(self, embedding_model: SemanticEmbeddingModel = None, vector_store: SemanticVectorStore = None):
        self.embedding_model = embedding_model or SemanticEmbeddingModel()
        self.vector_store = vector_store or SemanticVectorStore()

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Execute semantic vector search for a user query.
        """
        k = top_k or config.TOP_K
        if not query or not query.strip():
            return []

        query_vector = self.embedding_model.embed_text(query)
        raw_matches = self.vector_store.query(query_vector, top_k=k)
        return raw_matches
