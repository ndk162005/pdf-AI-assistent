from typing import List, Dict, Any, Tuple

class ContextBuilder:
    """Formats retrieved document chunks into clean LLM context and structured sources list."""

    @staticmethod
    def build_context(retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Build clean prompt context and source references list.

        Args:
            retrieved_chunks: List of chunk metadata dictionaries.

        Returns:
            Tuple[str, List[Dict[str, Any]]]: Context string and structured sources list.
        """
        if not retrieved_chunks:
            return "", []

        context_parts = []
        sources = []

        for idx, chunk in enumerate(retrieved_chunks, 1):
            filename = chunk.get("filename", "Unknown Document")
            page_number = chunk.get("page_number", "Unknown Page")
            text = chunk.get("chunk_text", "").strip()

            context_parts.append(
                f"--- Source [{idx}] (Document: {filename}, Page: {page_number}) ---\n{text}"
            )

            sources.append({
                "source_num": idx,
                "document": filename,
                "page": page_number,
                "text": text,
                "doc_id": chunk.get("doc_id", ""),
                "chunk_id": chunk.get("chunk_id", "")
            })

        full_context = "\n\n".join(context_parts)
        return full_context, sources
