import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
import config

class SemanticVectorStore:
    """ChromaDB Persistent Vector Store exclusively for the Semantic Search subsystem."""

    def __init__(self, vector_db_path: Optional[Path] = None):
        self.db_path = vector_db_path or config.SEMANTIC_VECTOR_DB_PATH
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="semantic_search_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add text chunks and embeddings to the semantic vector collection.
        """
        if not chunks or not embeddings:
            return

        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["chunk_text"] for chunk in chunks]
        metadatas = [
            {
                "doc_id": chunk["doc_id"],
                "filename": chunk["filename"],
                "page_number": int(chunk["page_number"]),
                "chunk_id": chunk["chunk_id"]
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query vector store for top_k nearest chunks and distance metrics.
        """
        if not query_embedding:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        matched_chunks = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            ids = results["ids"][0]
            documents = results["documents"][0] if results.get("documents") else []
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []

            for i in range(len(ids)):
                matched_chunks.append({
                    "chunk_id": ids[i],
                    "chunk_text": documents[i] if i < len(documents) else "",
                    "doc_id": metadatas[i].get("doc_id", "") if i < len(metadatas) else "",
                    "filename": metadatas[i].get("filename", "") if i < len(metadatas) else "",
                    "page_number": metadatas[i].get("page_number", 1) if i < len(metadatas) else 1,
                    "distance": distances[i] if i < len(distances) else 0.0
                })

        return matched_chunks

    def delete_document_chunks(self, doc_id: str):
        """
        Delete all vector entries belonging to a given document.
        """
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception:
            pass
