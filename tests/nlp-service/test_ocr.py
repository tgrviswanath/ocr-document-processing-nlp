import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MOCK_DOC_RESULT = {
    "doc_id": "test-uuid-1234",
    "filename": "test.pdf",
    "pages": 2,
    "source": "pymupdf",
    "avg_confidence": 100.0,
    "word_count": 150,
    "char_count": 900,
    "entities": [
        {"text": "John Smith", "label": "PERSON", "description": "People, including fictional"},
        {"text": "Acme Corp", "label": "ORG", "description": "Companies, agencies, institutions"},
    ],
    "text_preview": "This is a sample document about John Smith from Acme Corp.",
}

MOCK_QUERY_RESULT = {
    "doc_id": "test-uuid-1234",
    "question": "Who is mentioned?",
    "answer": "John Smith from Acme Corp is mentioned.",
    "source_chunks": [{"chunk": "John Smith from Acme Corp.", "score": 0.92}],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("app.core.service.process_document", return_value=MOCK_DOC_RESULT)
def test_upload_pdf(mock_proc):
    r = client.post(
        "/api/v1/nlp/upload",
        files={"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["doc_id"] == "test-uuid-1234"
    assert data["pages"] == 2
    assert len(data["entities"]) == 2


def test_upload_unsupported_format():
    r = client.post(
        "/api/v1/nlp/upload",
        files={"file": ("data.csv", b"a,b,c", "text/csv")},
    )
    assert r.status_code == 400


def test_upload_empty_file():
    r = client.post(
        "/api/v1/nlp/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert r.status_code == 400


@patch("app.core.service.query_document", return_value=MOCK_QUERY_RESULT)
def test_query(mock_query):
    r = client.post(
        "/api/v1/nlp/query",
        json={"doc_id": "test-uuid-1234", "question": "Who is mentioned?"},
    )
    assert r.status_code == 200
    assert "answer" in r.json()
    assert "source_chunks" in r.json()


def test_query_empty_question():
    r = client.post(
        "/api/v1/nlp/query",
        json={"doc_id": "test-uuid-1234", "question": "  "},
    )
    assert r.status_code == 400


def test_query_missing_doc():
    r = client.post(
        "/api/v1/nlp/query",
        json={"doc_id": "nonexistent-id", "question": "What is this?"},
    )
    assert r.status_code == 404


def test_clean_text_extraction():
    from app.core.ner import extract_entities
    with patch("app.core.ner._get_nlp") as mock_nlp:
        mock_doc = MagicMock()
        mock_doc.ents = []
        mock_nlp.return_value = MagicMock(return_value=mock_doc)
        result = extract_entities("Hello world")
        assert isinstance(result, list)
