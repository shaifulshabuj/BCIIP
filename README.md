# Bangladesh Continuous Internet Intelligence Platform (BCIIP)

A robust, modular platform for gathering, processing, and analyzing internet content from Bangladesh sources. The system features a continuous crawler, an NLP processing pipeline (including Bangla language support), vector-based semantic search, and a scheduled execution engine.

## Features

- **Ingestion**: 
  - Automated crawling of RSS feeds (Prothom Alo, The Daily Star, etc.).
  - Raw content storage in MinIO.
  - Metadata storage in PostgreSQL.

- **Processing Pipeline**:
  - **Normalization**: HTML cleaning and PDF text extraction.
  - **Language Detection**: FastText (Bangla/English).
  - **Categorization**: Rule-based topic classification.
  - **Entity Extraction**: Rule-based extraction of Persons, Locations, Organizations.
  - **Summarization**: Extractive summarization (TextRank/LSA).
  - **Embeddings**: Vector generation using `sentence-transformers` (all-MiniLM-L6-v2).

- **Search & API**:
  - **Semantic Search**: Vector similarity search using `pgvector`.
  - **REST API**: FastAPI endpoints for articles, search, and filtering.

- **Automation**:
  - **Scheduling**: Celery Beat for periodic tasks.
  - **Resilience**: Celery Worker with retry logic and Redis backing.

## Architecture

- **PostgreSQL**: Primary database (Metadata + Vector Embeddings).
- **MinIO**: Object storage for raw HTML/PDF files.
- **Redis**: Message broker and result backend for Celery.
- **API**: FastAPI application.
- **Worker**: Celery worker for processing tasks.
- **Beat**: Celery scheduler.

## Prerequisites

- Docker & Docker Compose
- 5GB+ Free Disk Space (for ML models and DB)

## Setup & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shaifulshabuj/BCIIP.git
   cd BCIIP
   ```

2. **Start the system**:
   ```bash
   docker-compose up -d --build
   ```

3. **Verify running services**:
   ```bash
   docker-compose ps
   ```

4. **Access the API**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - API Root: [http://localhost:8000](http://localhost:8000)

## API Usage

- **List Articles**: `GET /articles`
- **Search (Text)**: `GET /search?q=politics&type=text`
- **Semantic Search**: `GET /search?q=climate change&type=semantic`
- **Filter by Topic**: `GET /topics/politics`

## Development

- **Run Verification**:
  ```bash
  docker-compose exec api python scripts/verify_all.py
  ```

- **Rebuild specific service**:
  ```bash
  docker-compose up -d --build api
  ```

## License
Internal Project.
