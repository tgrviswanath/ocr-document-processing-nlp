# Project 17 - OCR Document Processing

Microservice NLP system that extracts text from scanned images and PDFs using Tesseract OCR, identifies named entities with spaCy, and enables semantic Q&A over the document using FAISS + Ollama.

## Architecture

```
Frontend :3000  →  Backend :8000  →  NLP Service :8001
  React/MUI        FastAPI/httpx      Tesseract + spaCy + FAISS + Ollama
```

## What's Different from Previous Projects

| Project | Input | NLP | Output |
|---------|-------|-----|--------|
| 1 | Text | NLTK | Sentiment |
| 3 | PDF | spaCy NER | Structured JSON |
| 15 | Audio | Whisper + BART | Summary + Tasks |
| 16 | Text | TF-IDF + LogReg | Fake/Real |
| **17** | **Image / PDF** | **Tesseract + spaCy + FAISS + Ollama** | **Entities + Q&A** |

## NLP Service - Pipeline

| Step | Tool | What it does |
|------|------|-------------|
| Image preprocessing | OpenCV | Denoise + threshold for better OCR |
| OCR (images) | Tesseract | Image → raw text |
| OCR (PDFs) | PyMuPDF | Native text extraction; Tesseract fallback for scanned pages |
| NER | spaCy en_core_web_sm | Extract PERSON, ORG, DATE, MONEY, GPE, etc. |
| Embedding | sentence-transformers (all-MiniLM-L6-v2) | Chunk text → vectors |
| Semantic search | FAISS IndexFlatIP | Find top-K relevant chunks for a query |
| Q&A | Ollama (llama3.2) | Generate answer from retrieved chunks |
| Fallback | Top chunk | If Ollama unavailable, returns best matching chunk |

## Local Run

```bash
# Prerequisites - install Tesseract
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux:   sudo apt install tesseract-ocr

# Optional - install Ollama for LLM Q&A
# https://ollama.ai  →  ollama pull llama3.2

# Terminal 1 - NLP Service
cd nlp-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- NLP Service: http://localhost:8001/docs
- Backend API: http://localhost:8000/docs
- Frontend UI: http://localhost:3000

## UI Features (3-tab workflow)

1. **Upload** — drag & drop PDF, PNG, JPG, TIFF, BMP, WEBP
2. **Results & Entities** — stats (pages, words, OCR engine), NER table grouped by type, extracted text preview
3. **Ask Questions** — semantic Q&A with source chunk citations and relevance scores

## Notes

- Documents are stored in-memory per session (cleared on service restart)
- Ollama is optional — fallback returns the most relevant chunk directly
- 8GB RAM sufficient for all-MiniLM-L6-v2 + spaCy
