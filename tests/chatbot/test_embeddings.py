import pytest
from app.chatbot.embeddings.embedding import ChatbotEmbeddingModel

def test_chatbot_embeddings_single_text():
    embedder = ChatbotEmbeddingModel()
    vec = embedder.embed_text("Test query embedding")
    assert isinstance(vec, list)
    assert len(vec) > 0
    assert isinstance(vec[0], float)

def test_chatbot_embeddings_multiple_texts():
    embedder = ChatbotEmbeddingModel()
    vecs = embedder.embed_documents(["Chunk one text", "Chunk two text"])
    assert isinstance(vecs, list)
    assert len(vecs) == 2
    assert len(vecs[0]) > 0

def test_chatbot_embeddings_empty():
    embedder = ChatbotEmbeddingModel()
    assert embedder.embed_text("") == []
    assert embedder.embed_documents([]) == []
