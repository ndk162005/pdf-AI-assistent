import pytest
import pymupdf as fitz
from pathlib import Path
from app.semantic_search.processing.pdf_extractor import SemanticPDFExtractor, SemanticPDFExtractionError
from app.semantic_search.processing.document_processor import SemanticDocumentProcessor

def create_sample_pdf(tmp_path: Path, filename: str = "semantic.pdf") -> Path:
    pdf_path = tmp_path / filename
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Semantic search engine document content.")
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_semantic_pdf_extractor(tmp_path):
    pdf_path = create_sample_pdf(tmp_path)
    extractor = SemanticPDFExtractor(pdf_path)
    pages = extractor.extract()
    assert len(pages) == 1
    assert "Semantic search engine" in pages[0]["text"]

def test_semantic_document_processor():
    processor = SemanticDocumentProcessor(chunk_size=50, chunk_overlap=10)
    pages_data = [{"text": "Semantic content text page.", "page_number": 1, "filename": "sem.pdf"}]
    chunks = processor.process_document(doc_id="sem_doc_1", pages_data=pages_data)
    assert len(chunks) > 0
    assert chunks[0]["doc_id"] == "sem_doc_1"
    assert "chunk_id" in chunks[0]
