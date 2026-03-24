"""
In-memory document store: holds OCR result + FAISS index per session.
Keyed by doc_id (UUID). Cleared on service restart.
"""
import uuid
from app.core.ocr import extract_from_image, extract_from_pdf
from app.core.ner import extract_entities
from app.core.search import build_index, search
from app.core.qa import answer
from app.core.config import settings

# { doc_id: { "text", "pages", "source", "entities", "index", "chunks", "embedder" } }
_store: dict = {}


def process_document(filename: str, file_bytes: bytes) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        ocr_result = extract_from_pdf(file_bytes)
    elif ext in {"png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"}:
        ocr_result = extract_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

    text = ocr_result["text"]
    entities = extract_entities(text)
    index, chunks, embedder = build_index(text)

    doc_id = str(uuid.uuid4())
    _store[doc_id] = {
        "text": text,
        "pages": ocr_result["pages"],
        "source": ocr_result["source"],
        "avg_confidence": ocr_result["avg_confidence"],
        "entities": entities,
        "index": index,
        "chunks": chunks,
        "embedder": embedder,
        "filename": filename,
    }

    return {
        "doc_id": doc_id,
        "filename": filename,
        "pages": ocr_result["pages"],
        "source": ocr_result["source"],
        "avg_confidence": ocr_result["avg_confidence"],
        "word_count": len(text.split()),
        "char_count": len(text),
        "entities": entities,
        "text_preview": text[:500],
    }


def query_document(doc_id: str, question: str) -> dict:
    doc = _store.get(doc_id)
    if not doc:
        raise KeyError(f"Document {doc_id} not found. Please upload again.")

    chunks = search(
        doc["index"], doc["chunks"], doc["embedder"],
        question, settings.TOP_K,
    )
    response = answer(question, chunks)

    return {
        "doc_id": doc_id,
        "question": question,
        "answer": response,
        "source_chunks": chunks,
    }


def get_document(doc_id: str) -> dict:
    doc = _store.get(doc_id)
    if not doc:
        raise KeyError(f"Document {doc_id} not found.")
    return {
        "doc_id": doc_id,
        "filename": doc["filename"],
        "pages": doc["pages"],
        "source": doc["source"],
        "word_count": len(doc["text"].split()),
        "entities": doc["entities"],
        "text": doc["text"],
    }
