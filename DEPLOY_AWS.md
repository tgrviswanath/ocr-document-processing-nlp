# AWS Deployment Guide — Project 17 OCR Document Processing

---

## AWS Services for OCR Document Processing

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Textract**        | OCR for images and PDFs — replace Tesseract + OpenCV + PyMuPDF               | Replace your entire OCR pipeline                   |
| **Amazon Comprehend**      | NER for PERSON, ORG, DATE, MONEY, LOCATION from extracted text               | Replace your spaCy NER pipeline                    |
| **Amazon Bedrock KB**      | Semantic Q&A over extracted document text — replace FAISS + Ollama           | Replace your FAISS + Ollama Q&A pipeline           |

> **Amazon Textract** is the direct replacement for your Tesseract + OpenCV pipeline. It handles scanned images, PDFs, tables, and forms with no preprocessing required.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + nlp-service containers in a private VPC               | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images/PDFs and extracted text results                     |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track OCR latency, entity counts, request volume                          |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Textract + Comprehend       │
│ NLP Service :8001 │    │ + Bedrock KB (Q&A)                 │
│ Tesseract+spaCy   │    │ No Tesseract install needed        │
│ +FAISS+Ollama     │    │                                    │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name ocrdoc/nlp-service --region $AWS_REGION
aws ecr create-repository --repository-name ocrdoc/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.nlp-service -t $ECR/ocrdoc/nlp-service:latest ./nlp-service
docker push $ECR/ocrdoc/nlp-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/ocrdoc/backend:latest ./backend
docker push $ECR/ocrdoc/backend:latest
```

---

## Step 2 — Create S3 Bucket for Documents

```bash
aws s3 mb s3://ocr-documents-$AWS_ACCOUNT --region $AWS_REGION
```

---

## Step 3 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name ocrdoc-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/ocrdoc/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "NLP_SERVICE_URL": "http://nlp-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Textract + Comprehend

```python
import boto3

textract = boto3.client("textract", region_name="eu-west-2")
comprehend = boto3.client("comprehend", region_name="eu-west-2")

def process_document(file_bytes: bytes) -> dict:
    # OCR
    text_response = textract.detect_document_text(Document={"Bytes": file_bytes})
    text = " ".join([b["Text"] for b in text_response["Blocks"] if b["BlockType"] == "LINE"])
    # NER
    entities_response = comprehend.detect_entities(Text=text[:5000], LanguageCode="en")
    entities = {}
    for entity in entities_response["Entities"]:
        entities.setdefault(entity["Type"], []).append({
            "text": entity["Text"],
            "confidence": round(entity["Score"] * 100, 2)
        })
    return {
        "text": text,
        "word_count": len(text.split()),
        "entities": entities,
        "entity_count": sum(len(v) for v in entities.values())
    }
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (nlp-service)   | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Textract            | Pay per page      | ~$1.50/1000 pages  |
| Amazon Comprehend          | Pay per unit      | ~$1–3/month        |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$24–35/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name ocrdoc/backend --force
aws ecr delete-repository --repository-name ocrdoc/nlp-service --force
aws s3 rm s3://ocr-documents-$AWS_ACCOUNT --recursive
aws s3 rb s3://ocr-documents-$AWS_ACCOUNT
```
