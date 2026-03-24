import httpx
from app.core.config import settings

NLP_URL = settings.NLP_SERVICE_URL


async def upload_document(filename: str, content: bytes, content_type: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/upload",
            files={"file": (filename, content, content_type)},
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()


async def query_document(doc_id: str, question: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/query",
            json={"doc_id": doc_id, "question": question},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json()


async def get_document(doc_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{NLP_URL}/api/v1/nlp/document/{doc_id}",
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()
