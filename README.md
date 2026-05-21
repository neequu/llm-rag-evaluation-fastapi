# Local RAG Retrieval Strategy Evaluation

A Retrieval-Augmented Generation (RAG) system and benchmarking framework for evaluating sparse, dense, and hybrid retrieval strategies under local CPU-only deployment constraints.

This project was developed as part of a bachelor's thesis focused on analyzing the trade-offs between retrieval quality and end-to-end latency in fully local RAG pipelines.

---

## Overview

The system implements three interchangeable retrieval pipelines:

- **BM25 sparse retrieval**
- **Dense vector retrieval**
- **Hybrid retrieval**
  - BM25
  - Dense retrieval
  - Reciprocal Rank Fusion (RRF)
  - Cross-encoder reranking

The application exposes FastAPI endpoints for:
- document ingestion
- retrieval
- RAG question answering
- workspace management
- authentication

All inference runs locally using Ollama and a lightweight language model (`phi4-mini`) without GPU acceleration.

---

## Thesis Focus

This project evaluates:

- retrieval effectiveness
- ranking quality
- end-to-end latency
- CPU-only inference feasibility

The evaluation compares:
- BM25
- Dense retrieval
- Hybrid retrieval

using:
- Precision@k
- Recall@k
- Hit@k
- Mean Reciprocal Rank (MRR)
- retrieval latency
- generation latency

---

## Architecture

```text
User Query
    ↓
Retrieval Strategy
    ├── BM25
    ├── Dense Retrieval
    └── Hybrid Retrieval
            ├── BM25
            ├── Dense
            ├── RRF Fusion
            └── Cross-Encoder Reranking
    ↓
Retrieved Chunks
    ↓
Prompt Construction
    ↓
Ollama (Phi-4-mini)
    ↓
Generated Answer
````

---

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL + pgvector
* Redis
* Alembic

### Retrieval / NLP

* ChromaDB
* Sentence Transformers
* rank-bm25
* Cross-Encoder reranking
* Ollama

### Storage

* MinIO (S3-compatible object storage)

### Evaluation

* Pandas
* Matplotlib

### Infrastructure

* Docker Compose

---

## Retrieval Strategies

### 1. BM25 Sparse Retrieval

Implemented using:

* `rank-bm25`

Uses lexical keyword matching.

---

### 2. Dense Retrieval

Implemented using:

* `all-MiniLM-L6-v2`
* ChromaDB cosine similarity search

Uses semantic vector similarity.

---

### 3. Hybrid Retrieval

Combines:

* BM25
* Dense retrieval
* Reciprocal Rank Fusion (RRF)

Final candidates are reranked using:

* `cross-encoder/ms-marco-MiniLM-L-6-v2`

---

## Project Structure

```text
app/
├── api/                # FastAPI endpoints
├── core/               # Configuration and infrastructure
├── crud/               # Database access layer
├── db/                 # Database setup
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── services/           # Retrieval and RAG logic
├── workers/            # Background ingestion workers

evaluation/
├── plots/              # Generated evaluation figures
├── results.json        # Raw experiment outputs
├── retrieval_metrics.csv
├── additional_retrieval_metrics.csv

scripts/
├── run_evaluation.py
├── compute_retrieval_metrics.py
├── compute_additional_retrieval_metrics.py
├── create_evaluation_plots.py
```

---

## Requirements

* Docker
* Docker Compose
* Python 3.13+
* Ollama

---

## Setup

### 1. Clone repository

```bash
git clone <repository-url>
cd llm-rag-evaluation
```

---

### 2. Create environment file

Create:

```text
.env.docker
```

Example configuration:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=fastapi_db

APP_PORT=8000

OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=phi4-mini

CHROMA_HOST=chromadb
CHROMA_PORT=8000
```

---

### 3. Start services

```bash
docker compose up --build
```

This starts:

* FastAPI application
* PostgreSQL
* Redis
* MinIO
* ChromaDB
* Ollama

---

### 4. Pull Ollama model

```bash
docker exec -it <ollama-container> ollama pull phi4-mini
```

---

## Running Database Migrations

```bash
alembic upgrade head
```

---

## API Documentation

After startup:

* Swagger UI:

  ```text
  http://localhost:8000/docs
  ```

* ReDoc:

  ```text
  http://localhost:8000/redoc
  ```

---

## Running Evaluation

### Step 1 — Generate evaluation results

```bash
python scripts/run_evaluation.py
```

Output:

```text
evaluation/results.json
```

---

### Step 2 — Compute retrieval metrics

```bash
python scripts/compute_retrieval_metrics.py
```

Outputs:

```text
evaluation/retrieval_metrics.csv
```

Metrics:

* Precision@k
* Recall@k
* latency breakdown

---

### Step 3 — Compute additional ranking metrics

```bash
python scripts/compute_additional_retrieval_metrics.py
```

Outputs:

```text
evaluation/additional_retrieval_metrics.csv
evaluation/additional_retrieval_metrics_summary.csv
```

Metrics:

* Hit@k
* MRR

---

### Step 4 — Generate plots

```bash
python scripts/create_evaluation_plots.py
```

Outputs:

```text
evaluation/plots/
```

Generated figures:

* Precision@k
* Recall@k
* Hit@k
* MRR
* latency comparison
* metrics by question type

---

## Evaluation Dataset

The benchmark dataset consists of:

* FastAPI documentation pages
* manually created evaluation queries
* factual
* procedural
* conceptual question categories

Each query contains:

* reference answer
* expected chunk IDs
* question type

---

## Hardware Constraints

Experiments were conducted on:

* CPU-only hardware
* no GPU acceleration
* consumer-grade laptop environment

The project intentionally focuses on reproducible local deployment scenarios rather than server-scale infrastructure.

---

## Example Results

| Strategy | Precision@k | Recall@k | MRR    |
| -------- | ----------- | -------- | ------ |
| BM25     | 0.1441      | 0.3378   | 0.1423 |
| Dense    | 0.1622      | 0.4189   | 0.1362 |
| Hybrid   | 0.2252      | 0.5405   | 0.2317 |

Key observation:

* Hybrid retrieval achieved the strongest retrieval quality.
* Generation latency dominated total runtime under CPU-only inference constraints.

---

## Future Improvements

Potential extensions:

* ANN indexing (HNSW)
* GPU inference
* larger evaluation datasets
* streaming generation
* prompt compression
* adaptive retrieval depth

---

## License

MIT License

---

## Author

Bachelor Thesis Project
Applied AI / Retrieval-Augmented Generation Research

