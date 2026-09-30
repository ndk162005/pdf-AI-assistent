from dataclasses import dataclass
from typing import Optional

@dataclass
class SemanticDocumentRecord:
    document_id: str
    filename: str
    filepath: str
    total_pages: int
    created_at: str

@dataclass
class SemanticChunkRecord:
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    chunk_text: str
    created_at: Optional[str] = None
