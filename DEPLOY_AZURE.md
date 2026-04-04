# Azure Deployment Guide — Project 17 OCR Document Processing

---

## Azure Services for OCR Document Processing

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Document Intelligence**   | OCR for images and PDFs — replace Tesseract + OpenCV + PyMuPDF               | Replace your entire OCR pipeline                   |
| **Azure AI Language — NER**          | Extract PERSON, ORG, DATE, MONEY, LOCATION from extracted text               | Replace your spaCy NER pipeline                    |
| **Azure OpenAI Service**             | GPT-4 for semantic Q&A over extracted document text — replace FAISS + Ollama | Replace your FAISS + Ollama Q&A pipeline           |

> **Azure AI Document Intelligence** is the direct replacement for your Tesseract + OpenCV pipeline. It handles scanned images, PDFs, tables, and forms with no preprocessing required.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, nlp-service)       | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images/PDFs and extracted text results                    |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track OCR latency, entity counts, request volume                     |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure AI Document Intelligence     │
│ NLP Service :8001 │    │ + Azure AI Language NER            │
│ Tesseract+spaCy   │    │ + Azure OpenAI (Q&A)               │
│ +FAISS+Ollama     │    │ No Tesseract install needed        │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-ocr-doc --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-ocr-doc --name ocrdocacr --sku Basic --admin-enabled true
az acr login --name ocrdocacr
ACR=ocrdocacr.azurecr.io
docker build -f docker/Dockerfile.nlp-service -t $ACR/nlp-service:latest ./nlp-service
docker push $ACR/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Create Blob Storage for Documents

```bash
az storage account create --name ocrdocfiles --resource-group rg-ocr-doc --sku Standard_LRS
az storage container create --name documents --account-name ocrdocfiles
az storage container create --name results --account-name ocrdocfiles
```

---

## Step 3 — Deploy Container Apps

```bash
az containerapp env create --name ocrdoc-env --resource-group rg-ocr-doc --location uksouth

az containerapp create \
  --name nlp-service --resource-group rg-ocr-doc \
  --environment ocrdoc-env --image $ACR/nlp-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-ocr-doc \
  --environment ocrdoc-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars NLP_SERVICE_URL=http://nlp-service:8001
```

---

## Option B — Use Azure AI Document Intelligence + Azure AI Language

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

doc_client = DocumentAnalysisClient(
    endpoint=os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_DOC_INTELLIGENCE_KEY"))
)
lang_client = TextAnalyticsClient(
    endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_LANGUAGE_KEY"))
)

def process_document(file_bytes: bytes) -> dict:
    poller = doc_client.begin_analyze_document("prebuilt-read", file_bytes)
    result = poller.result()
    text = result.content
    ner_result = lang_client.recognize_entities([text[:5120]])[0]
    entities = {}
    for entity in ner_result.entities:
        entities.setdefault(entity.category, []).append({
            "text": entity.text,
            "confidence": round(entity.confidence_score * 100, 2)
        })
    return {"text": text, "word_count": len(text.split()), "entities": entities}
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (nlp-svc) | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Doc Intelligence         | S0 tier   | Pay per page      |
| Azure AI Language        | S tier    | Pay per call      |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–25/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-ocr-doc --yes --no-wait
```
