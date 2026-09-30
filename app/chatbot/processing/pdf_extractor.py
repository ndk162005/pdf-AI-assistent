import pymupdf as fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Union

class PDFExtractionError(Exception):
    """Custom exception raised when PDF extraction fails."""
    pass

class ChatbotPDFExtractor:
    """PDF Extractor module dedicated to the AI PDF Chatbot pipeline."""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)

    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract text page by page from the PDF document.

        Returns:
            List[Dict[str, Any]]: List of extracted page data objects containing:
                - text: str
                - page_number: int (1-based)
                - filename: str
                - total_pages: int
        """
        if not self.file_path.exists():
            raise PDFExtractionError(f"PDF file does not exist: {self.file_path}")

        if self.file_path.stat().st_size == 0:
            raise PDFExtractionError(f"PDF file is empty: {self.file_path}")

        try:
            doc = fitz.open(self.file_path)
        except Exception as e:
            raise PDFExtractionError(f"Failed to open or parse corrupted PDF: {str(e)}")

        pages_data = []
        try:
            total_pages = doc.page_count
            if total_pages == 0:
                raise PDFExtractionError("PDF contains no pages.")

            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                text = page.get_text("text").strip()
                pages_data.append({
                    "text": text,
                    "page_number": page_idx + 1,
                    "filename": self.file_path.name,
                    "total_pages": total_pages
                })
        except Exception as e:
            if isinstance(e, PDFExtractionError):
                raise
            raise PDFExtractionError(f"Error extracting content from PDF: {str(e)}")
        finally:
            doc.close()

        return pages_data
