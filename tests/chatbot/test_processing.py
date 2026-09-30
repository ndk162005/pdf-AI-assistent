import pytest
import pymupdf as fitz
from pathlib import Path
from app.chatbot.processing.pdf_extractor import ChatbotPDFExtractor, PDFExtractionError
from app.chatbot.processing.document_processor import ChatbotDocumentProcessor

def create_sample_pdf(tmp_path: Path, filename: str = "sample.pdf", content: str = "Hello Chatbot World") -> Path:
    pdf_path = tmp_path / filename
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), content)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_chatbot_pdf_extractor_success(tmp_path):
    pdf_path = create_sample_pdf(tmp_path, "test.pdf", "Sample PDF text for extraction testing.")
    extractor = ChatbotPDFExtractor(pdf_path)
    pages = extractor.extract()
    assert len(pages) == 1
    assert "Sample PDF text" in pages[0]["text"]
    assert pages[0]["page_number"] == 1
    assert pages[0]["filename"] == "test.pdf"

def test_chatbot_pdf_extractor_non_existent():
    extractor = ChatbotPDFExtractor("non_existent_path.pdf")
    with pytest.raises(PDFExtractionError):
        extractor.extract()

def test_chatbot_document_processor():
    processor = ChatbotDocumentProcessor(chunk_size=50, chunk_overlap=10)
    pages_data = [{
        "text": "This is line one of the test pdf document. It contains multiple words to verify chunking.",
        "page_number": 1,
        "filename": "test.pdf"
    }]
    chunks = processor.process_document(doc_id="doc_123", pages_data=pages_data)
    assert len(chunks) > 0
    assert chunks[0]["doc_id"] == "doc_123"
    assert chunks[0]["filename"] == "test.pdf"
    assert "chunk_id" in chunks[0]
