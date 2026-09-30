import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer
import config

logger = logging.getLogger(__name__)

class ChatbotEmbeddingModel:
    """Embedding model wrapper for the AI Chatbot subsystem."""
    _instance = None
    _model = None

    def __new__(cls, model_name: str = None):
        if cls._instance is None:
            cls._instance = super(ChatbotEmbeddingModel, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = None):
        target_model = model_name or config.EMBEDDING_MODEL
        if ChatbotEmbeddingModel._model is None or getattr(self, "_current_model_name", None) != target_model:
            logger.info(f"Initializing Chatbot SentenceTransformer embedding model: {target_model}")
            ChatbotEmbeddingModel._model = SentenceTransformer(target_model)
            self._current_model_name = target_model

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single string query or chunk."""
        if not text:
            return []
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of document chunk texts."""
        if not texts:
            return []
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
