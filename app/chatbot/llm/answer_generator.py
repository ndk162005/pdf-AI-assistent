import logging
from typing import List, Dict, Any, Tuple
from app.chatbot.llm.ollama_client import OllamaClient, OllamaClientError
from app.chatbot.retrieval.context_builder import ContextBuilder

logger = logging.getLogger(__name__)

class AnswerGenerator:
    """Combines retrieved context and user query to generate grounded answers using Ollama LLM."""

    SYSTEM_PROMPT = (
        "You are an intelligent PDF Assistant. Answer the user's question accurately, directly, and thoroughly "
        "using the provided document context. Combine relevant facts across sources when appropriate. "
        "If the provided context does not contain enough information to answer the question, state clearly: "
        "'I couldn't find enough information in the uploaded documents to answer that question.' "
        "Do not invent facts not supported by the context."
    )

    def __init__(self, ollama_client: OllamaClient = None):
        self.ollama_client = ollama_client or OllamaClient()

    def generate_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate answer and return structured sources.

        Args:
            query: User's question.
            retrieved_chunks: Chunks retrieved by vector search.

        Returns:
            Tuple[str, List[Dict[str, Any]]]: Generated answer text and document sources.
        """
        context_str, sources = ContextBuilder.build_context(retrieved_chunks)

        is_greeting = query.strip().lower() in [
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "how are you", "who are you", "what can you do", "help"
        ]

        if is_greeting:
            return "Hello! I am your PDF AI Assistant. How can I help you with your documents today?", []

        if not retrieved_chunks or not context_str.strip():
            return "I couldn't find enough information in the uploaded documents to answer that question.", []

        prompt = (
            f"Retrieved Document Context:\n{context_str}\n\n"
            f"User Question: {query}\n\n"
            f"Instructions: Provide a clear, complete, and accurate answer based on the retrieved context above."
        )

        try:
            answer = self.ollama_client.generate(prompt=prompt, system_prompt=self.SYSTEM_PROMPT)
            if not answer or len(answer.strip()) == 0:
                answer = "I couldn't find enough information in the uploaded documents to answer that question."
            return answer, sources
        except OllamaClientError as e:
            logger.warning(f"Ollama integration warning: {str(e)}")
            # Fallback answer informing user about Ollama status while returning context sources
            fallback_msg = (
                f"[Ollama LLM Notice]: {str(e)}\n\n"
                f"However, relevant document content was retrieved. Please see the document sources below."
            )
            return fallback_msg, sources
