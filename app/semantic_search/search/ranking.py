from typing import List, Dict, Any

class ResultRanker:
    """Ranks and formats semantic search results with normalized similarity scores."""

    @staticmethod
    def rank_results(raw_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank matches by similarity score (descending) and assign rank indices.

        Args:
            raw_matches: List of match dictionaries containing 'distance', 'filename', etc.

        Returns:
            List[Dict[str, Any]]: Ranked results list with keys:
                rank, document, page, text, score
        """
        if not raw_matches:
            return []

        processed = []
        for item in raw_matches:
            distance = float(item.get("distance", 1.0))
            # Cosine distance to cosine similarity score formula
            similarity_score = max(0.0, min(1.0, 1.0 - distance))
            
            processed.append({
                "document": item.get("filename", "Unknown"),
                "page": item.get("page_number", 1),
                "text": item.get("chunk_text", ""),
                "raw_score": similarity_score,
                "doc_id": item.get("doc_id", ""),
                "chunk_id": item.get("chunk_id", "")
            })

        # Sort by similarity score descending
        processed.sort(key=lambda x: x["raw_score"], reverse=True)

        ranked_output = []
        for index, entry in enumerate(processed, 1):
            ranked_output.append({
                "rank": index,
                "document": entry["document"],
                "page": entry["page"],
                "text": entry["text"],
                "score": round(entry["raw_score"], 4)
            })

        return ranked_output
