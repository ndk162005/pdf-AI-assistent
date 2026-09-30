import uuid
from typing import List, Dict, Any

class ChatbotDocumentProcessor:
    """Document processing module for splitting PDF extracted pages into chunks for Chatbot indexing."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, doc_id: str, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process page data list into searchable text chunks.

        Args:
            doc_id: Unique document identifier.
            pages_data: List of extracted page data dictionaries.

        Returns:
            List[Dict[str, Any]]: Chunks list with metadata.
        """
        chunks = []
        chunk_counter = 0

        for page_info in pages_data:
            text = page_info.get("text", "")
            page_number = page_info.get("page_number", 1)
            filename = page_info.get("filename", "")

            if not text or len(text.strip()) == 0:
                continue

            page_chunks = self._chunk_text(text)
            for chunk_text in page_chunks:
                if not chunk_text.strip():
                    continue
                chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "filename": filename,
                    "page_number": page_number,
                    "chunk_text": chunk_text,
                })
                chunk_counter += 1

        return chunks

    def _chunk_text(self, text: str) -> List[str]:
        """Split a string into overlapping character/word chunks."""
        words = text.split()
        if not words:
            return []

        chunks = []
        current_chunk_words = []
        current_length = 0

        for word in words:
            word_len = len(word) + 1  # count space
            if current_length + word_len > self.chunk_size and current_chunk_words:
                chunks.append(" ".join(current_chunk_words))
                
                # Calculate overlap in words
                overlap_words = []
                overlap_length = 0
                for w in reversed(current_chunk_words):
                    if overlap_length + len(w) + 1 <= self.chunk_overlap:
                        overlap_words.insert(0, w)
                        overlap_length += len(w) + 1
                    else:
                        break
                
                current_chunk_words = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk_words)
            else:
                current_chunk_words.append(word)
                current_length += word_len

        if current_chunk_words:
            chunks.append(" ".join(current_chunk_words))

        return chunks
