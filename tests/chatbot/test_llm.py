from unittest.mock import MagicMock
from app.chatbot.llm.ollama_client import OllamaClient
from app.chatbot.llm.answer_generator import AnswerGenerator

def test_answer_generator_with_mock_client():
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = "The port entry requirements specify a 24h notice."

    generator = AnswerGenerator(ollama_client=mock_ollama)
    chunks = [
        {"filename": "rules.pdf", "page_number": 3, "chunk_text": "Port requires 24h notice.", "doc_id": "d1", "chunk_id": "c1"}
    ]
    answer, sources = generator.generate_answer("What are the port entry requirements?", chunks)
    assert "24h notice" in answer
    assert len(sources) == 1
    assert sources[0]["document"] == "rules.pdf"

def test_answer_generator_insufficient_context():
    generator = AnswerGenerator()
    answer, sources = generator.generate_answer("What is the speed limit?", [])
    assert "couldn't find enough information" in answer
    assert sources == []
