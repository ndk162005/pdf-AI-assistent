import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import config
from app.chatbot.database.models import DocumentRecord, ChunkRecord

class ChatbotDatabase:
    """SQLite Database manager exclusively for the Chatbot subsystem."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.CHATBOT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    total_pages INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_chunks_doc_id ON chunks (document_id);")
            conn.commit()

    def save_document(self, doc_record: DocumentRecord):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents (document_id, filename, filepath, total_pages, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_record.document_id, doc_record.filename, doc_record.filepath, doc_record.total_pages, doc_record.created_at))
            conn.commit()

    def save_chunks(self, chunk_records: List[ChunkRecord]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.executemany("""
                INSERT OR REPLACE INTO chunks (chunk_id, document_id, filename, page_number, chunk_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [(c.chunk_id, c.document_id, c.filename, c.page_number, c.chunk_text, now) for c in chunk_records])
            conn.commit()

    def get_all_documents(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT document_id, filename, filepath, total_pages, created_at FROM documents ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT document_id, filename, filepath, total_pages, created_at FROM documents WHERE document_id = ?", (document_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_document(self, document_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            conn.commit()
