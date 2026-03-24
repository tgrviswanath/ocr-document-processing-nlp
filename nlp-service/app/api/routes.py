from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.core.service import process_document, query_document, get_document

router = APIRouter(prefix="/api/v1/nlp", tags=["ocr"])

ALLOWED_EXTS = {"pdf", "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"}


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
    try:
        return process_document(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/query")
def query(body: QueryInput):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    try:
        return query_document(body.doc_id, body.question)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/document/{doc_id}")
def get_doc(doc_id: str):
    try:
        return get_document(doc_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
