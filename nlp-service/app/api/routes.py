import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.core.service import process_document, query_document, get_document

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTS = {"pdf", "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"}

router = APIRouter(prefix="/api/v1/nlp", tags=["ocr"])


class QueryInput(BaseModel):
    doc_id: str
    question: str


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 50MB")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, process_document, file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query(body: QueryInput):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, query_document, body.doc_id, body.question)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{doc_id}")
def get_doc(doc_id: str):
    try:
        return get_document(doc_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
