"""
Q&A via Ollama LLM using retrieved context chunks.
Falls back to returning top chunk if Ollama is unavailable.
"""
import ollama
from app.core.config import settings

_PROMPT = """You are a helpful assistant answering questions about a document.
Use ONLY the context below to answer. If the answer is not in the context, say "Not found in document."

Context:
{context}

Question: {question}

Answer:"""


def answer(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant content found in the document."

    context = "\n\n".join(c["chunk"] for c in chunks[:3])
    prompt = _PROMPT.format(context=context, question=question)

    try:
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()
    except Exception:
        # Fallback: return the most relevant chunk directly
        return chunks[0]["chunk"]
