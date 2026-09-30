from typing import List, Dict, Any
from app.chatbot.embeddings.embedding import ChatbotEmbeddingModel
from app.chatbot.database.vector_store import ChatbotVectorStore
import config

class ChatbotRetriever:
    """Retrieval module for Chatbot pipeline."""

    def __init__(self, embedding_model: ChatbotEmbeddingModel = None, vector_store: ChatbotVectorStore = None):
        self.embedding_model = embedding_model or ChatbotEmbeddingModel()
        self.vector_store = vector_store or ChatbotVectorStore()

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a user query.
        """
        k = top_k or config.TOP_K
        if not query or not query.strip():
            return []

        query_vector = self.embedding_model.embed_text(query)
        chunks = self.vector_store.query(query_vector, top_k=k)
        return chunks
