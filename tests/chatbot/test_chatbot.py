from unittest.mock import MagicMock
from app.chatbot.database.database import ChatbotDatabase
from app.chatbot.database.vector_store import ChatbotVectorStore
from app.chatbot.retrieval.retrieval import ChatbotRetriever
from app.chatbot.llm.answer_generator import AnswerGenerator
from app.chatbot.llm.ollama_client import OllamaClient

def test_complete_chatbot_flow(tmp_path):
    # Setup temporary databases
    db_path = tmp_path / "chatbot.db"
    vdb_path = tmp_path / "vdb"
    
    db = ChatbotDatabase(db_path=db_path)
    vstore = ChatbotVectorStore(vector_db_path=vdb_path)

    # Ingest mock chunks
    chunk_data = [
        {"chunk_id": "c1", "doc_id": "d1", "filename": "vessel.pdf", "page_number": 1, "chunk_text": "Vessel must report arrival 24 hours prior."}
    ]
    # Simple dummy vector
    vstore.add_chunks(chunk_data, [[0.05] * 384])

    # Retrieve
    retriever = ChatbotRetriever(vector_store=vstore)
    retrieved = retriever.retrieve("When to report arrival?", top_k=1)
    assert len(retrieved) == 1

    # Mock Ollama response
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = "Report arrival 24 hours prior."

    ans_gen = AnswerGenerator(ollama_client=mock_ollama)
    answer, sources = ans_gen.generate_answer("When to report arrival?", retrieved)

    assert "24 hours prior" in answer
    assert sources[0]["document"] == "vessel.pdf"
