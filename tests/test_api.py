import pymupdf as fitz
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "PDF AI Assistant"

def test_upload_invalid_file_type():
    response = client.post("/api/upload", files={"file": ("test.txt", b"Hello text", "text/plain")})
    assert response.status_code == 400
    assert "Only PDF files" in response.json()["detail"]

def test_upload_corrupted_pdf():
    response = client.post("/api/upload", files={"file": ("test.pdf", b"Not a real pdf header", "application/pdf")})
    assert response.status_code == 400
    assert "not a valid PDF document" in response.json()["detail"]

def test_upload_and_query_flow(tmp_path):
    # Create valid sample PDF bytes
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "The official vessel speed limit in harbor channels is 10 knots.")
    pdf_bytes = doc.tobytes()
    doc.close()

    # Upload PDF
    upload_res = client.post("/api/upload", files={"file": ("speed_rules.pdf", pdf_bytes, "application/pdf")})
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    doc_id = upload_data["document_id"]
    assert doc_id is not None
    assert upload_data["filename"] == "speed_rules.pdf"

    # Query
    query_res = client.post("/api/query", json={"query": "What is the vessel speed limit?", "top_k": 5})
    assert query_res.status_code == 200
    query_data = query_res.json()
    
    assert "chatbot" in query_data
    assert "semantic_search" in query_data
    assert "answer" in query_data["chatbot"]
    assert "results" in query_data["semantic_search"]

    # List documents
    docs_res = client.get("/api/documents")
    assert docs_res.status_code == 200
    assert docs_res.json()["count"] >= 1

    # Delete document
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["document_id"] == doc_id
