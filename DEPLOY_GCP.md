# GCP Deployment Guide — Project 17 OCR Document Processing

---

## GCP Services for OCR Document Processing

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Document AI**                | OCR for images and PDFs — replace Tesseract + OpenCV + PyMuPDF               | Replace your entire OCR pipeline                   |
| **Cloud Natural Language API**       | NER for PERSON, ORG, DATE, MONEY, LOCATION from extracted text               | Replace your spaCy NER pipeline                    |
| **Vertex AI Search**                 | Semantic Q&A over extracted document text — replace FAISS + Ollama           | Replace your FAISS + Ollama Q&A pipeline           |

> **Cloud Document AI** is the direct replacement for your Tesseract + OpenCV pipeline. It handles scanned images, PDFs, tables, and forms with no preprocessing required.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + nlp-service containers — serverless, scales to zero   | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images/PDFs and extracted text results                     |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track OCR latency, entity counts, request volume                          |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Cloud Document AI                  │
│ NLP Service :8001 │    │ + Cloud Natural Language NER       │
│ Tesseract+spaCy   │    │ + Vertex AI Search (Q&A)           │
│ +FAISS+Ollama     │    │ No Tesseract install needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create ocrdoc-project --name="OCR Document Processing"
gcloud config set project ocrdoc-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com language.googleapis.com \
  documentai.googleapis.com aiplatform.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create ocrdoc-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/ocrdoc-project/ocrdoc-repo
docker build -f docker/Dockerfile.nlp-service -t $AR/nlp-service:latest ./nlp-service
docker push $AR/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Create Cloud Storage for Documents

```bash
gsutil mb -l $GCP_REGION gs://ocr-documents-ocrdoc-project
```

---

## Step 3 — Deploy to Cloud Run

```bash
gcloud run deploy nlp-service \
  --image $AR/nlp-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

NLP_URL=$(gcloud run services describe nlp-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars NLP_SERVICE_URL=$NLP_URL
```

---

## Option B — Use Cloud Document AI + Cloud Natural Language API

```python
from google.cloud import documentai_v1 as documentai
from google.cloud import language_v1

doc_client = documentai.DocumentProcessorServiceClient()
lang_client = language_v1.LanguageServiceClient()

def process_document(file_bytes: bytes, mime_type: str = "application/pdf") -> dict:
    processor_name = "projects/ocrdoc-project/locations/eu/processors/<processor-id>"
    raw_document = documentai.RawDocument(content=file_bytes, mime_type=mime_type)
    result = doc_client.process_document(
        request=documentai.ProcessRequest(name=processor_name, raw_document=raw_document)
    )
    text = result.document.text
    # NER
    document = language_v1.Document(content=text[:5000], type_=language_v1.Document.Type.PLAIN_TEXT)
    ner_result = lang_client.analyze_entities(request={"document": document})
    entities = {}
    for entity in ner_result.entities:
        entity_type = language_v1.Entity.Type(entity.type_).name
        entities.setdefault(entity_type, []).append({"text": entity.name, "salience": round(entity.salience, 3)})
    return {"text": text, "word_count": len(text.split()), "entities": entities}
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (nlp-service)    | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Cloud Document AI          | Pay per page          | ~$1.50/1000 pages  |
| Cloud Natural Language API | 5k units free         | $0–pay per call    |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$13–20/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete nlp-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete ocrdoc-repo --location=$GCP_REGION --quiet
gsutil rm -r gs://ocr-documents-ocrdoc-project
gcloud projects delete ocrdoc-project
```
