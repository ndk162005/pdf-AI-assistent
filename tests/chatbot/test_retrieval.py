from app.chatbot.retrieval.context_builder import ContextBuilder
from app.chatbot.retrieval.retrieval import ChatbotRetriever

def test_context_builder():
    retrieved_chunks = [
        {"filename": "doc.pdf", "page_number": 2, "chunk_text": "Port entry details.", "doc_id": "d1", "chunk_id": "c1"}
    ]
    context_str, sources = ContextBuilder.build_context(retrieved_chunks)
    assert "Port entry details." in context_str
    assert "doc.pdf" in context_str
    assert len(sources) == 1
    assert sources[0]["document"] == "doc.pdf"
    assert sources[0]["page"] == 2

def test_context_builder_empty():
    context_str, sources = ContextBuilder.build_context([])
    assert context_str == ""
    assert sources == []
