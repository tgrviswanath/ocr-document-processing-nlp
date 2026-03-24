import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MOCK_UPLOAD = {
    "doc_id": "abc-123",
    "filename": "invoice.pdf",
    "pages": 1,
    "source": "pymupdf",
    "word_count": 80,
    "char_count": 500,
    "entities": [],
    "text_preview": "Invoice #1234 from Acme Corp.",
}

MOCK_QUERY = {
    "doc_id": "abc-123",
    "question": "What is the invoice number?",
    "answer": "Invoice #1234",
    "source_chunks": [{"chunk": "Invoice #1234 from Acme Corp.", "score": 0.95}],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.upload_document", new_callable=AsyncMock, return_value=MOCK_UPLOAD)
def test_upload(mock_upload):
    r = client.post(
        "/api/v1/upload",
        files={"file": ("invoice.pdf", b"fake pdf", "application/pdf")},
    )
    assert r.status_code == 200
    assert r.json()["doc_id"] == "abc-123"


@patch("app.core.service.query_document", new_callable=AsyncMock, return_value=MOCK_QUERY)
def test_query(mock_query):
    r = client.post(
        "/api/v1/query",
        json={"doc_id": "abc-123", "question": "What is the invoice number?"},
    )
    assert r.status_code == 200
    assert r.json()["answer"] == "Invoice #1234"


@patch("app.core.service.get_document", new_callable=AsyncMock, return_value=MOCK_UPLOAD)
def test_get_document(mock_get):
    r = client.get("/api/v1/document/abc-123")
    assert r.status_code == 200
    assert r.json()["filename"] == "invoice.pdf"
