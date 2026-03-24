from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.core.service import upload_document, query_document, get_document
import httpx

router = APIRouter(prefix="/api/v1", tags=["ocr"])


class QueryInput(BaseModel):
    doc_id: str
    question: str


def _handle(e: Exception):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="NLP service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return await upload_document(file.filename, content, file.content_type or "application/octet-stream")
    except Exception as e:
        _handle(e)


@router.post("/query")
async def query(body: QueryInput):
    try:
        return await query_document(body.doc_id, body.question)
    except Exception as e:
        _handle(e)


@router.get("/document/{doc_id}")
async def get_doc(doc_id: str):
    try:
        return await get_document(doc_id)
    except Exception as e:
        _handle(e)
