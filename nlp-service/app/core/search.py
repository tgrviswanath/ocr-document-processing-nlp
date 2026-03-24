"""
Semantic search: embeds document chunks into FAISS index,
then retrieves top-K relevant chunks for a query.
"""
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import settings

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder


def _chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """Split text into overlapping word chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def build_index(text: str) -> tuple:
    """Returns (faiss_index, chunks, embedder)."""
    embedder = _get_embedder()
    chunks = _chunk_text(text)
    if not chunks:
        return None, [], embedder
    embeddings = embedder.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product = cosine on normalized vecs
    index.add(embeddings.astype(np.float32))
    return index, chunks, embedder


def search(index, chunks: list[str], embedder, query: str, top_k: int) -> list[dict]:
    if index is None or not chunks:
        return []
    q_vec = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, indices = index.search(q_vec.astype(np.float32), min(top_k, len(chunks)))
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            results.append({
                "chunk": chunks[idx],
                "score": round(float(score), 4),
            })
    return results
