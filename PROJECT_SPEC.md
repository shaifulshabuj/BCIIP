# Bangladesh Continuous Internet Intelligence Platform (BCIIP)

## 1. Purpose

BCIIP is a continuous information collection and intelligence system focused exclusively on Bangladesh-related public internet content.

The system continuously:
- Collects data from approved sources
- Normalizes and validates content
- Categorizes and enriches content
- Stores raw + structured + searchable data
- Exposes APIs for search and analysis

This specification is written for **AI agent-driven development** and must be executed **phase-by-phase**.

---

## 2. Core Constraints

### 2.1 Agent Behavior Constraints (MANDATORY)

- Development MUST be **iterative and phase-locked**
- Do NOT start a phase until the previous phase:
  - Builds successfully
  - Has a runnable verification script
- Prefer **simple, testable implementations**
- Heavy ML models must be **mocked or API-based initially**
- Data must persist across container restarts
- No stub code (e.g., `pass`, empty methods)

---

## 3. Tech Stack (MVP-Safe)

### Backend
- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy

### Crawling
- Scrapy
- feedparser

### NLP (MVP MODE)
- Language detection: fastText (external model download script)
- Categorization: keyword + heuristic baseline
- Entities: rule-based (regex + dictionaries)
- Summarization: API-based (OpenAI / mock)

### Storage
- PostgreSQL
- MinIO (raw content)
- Qdrant (disabled until Phase 7)

### Task Processing
- Celery
- Redis

### DevOps
- Docker
- Docker Compose
- Poetry
- `.env`-based config

---

## 4. Repository Structure (Target)

bciip/
├── services/
│   ├── api/
│   ├── crawler/
│   ├── processor/
│   └── worker/
├── libs/
│   ├── text_cleaning/
│   ├── language_detection/
│   └── categorization/
├── scripts/
│   ├── verify_phase_0.py
│   ├── verify_phase_1.py
│   └── download_models.py
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── PROJECT_SPEC.md
└── README.md

---

## 5. Phase Definitions

---

## PHASE 0 – Repository & Environment Setup

### Objectives
- Initialize repo
- Setup Poetry
- Setup Docker & docker-compose
- Define service containers (no crawling yet)

### Requirements
- PostgreSQL container
- Redis container
- MinIO container
- FastAPI skeleton
- Environment builds successfully

### Verification
- `docker-compose up --build`
- `verify_phase_0.py` confirms DB & Redis connectivity

---

## PHASE 1 – Source Definition & Crawling (Minimal)

### Objectives
- Crawl Bangladesh news sources
- Store raw HTML/text only

### Sources (Initial)
- Prothom Alo (RSS)
- BDNews24 (RSS)
- The Daily Star (RSS)

### Requirements
- robots.txt respected
- URL deduplication
- Crawl logs visible

### Output
- Raw articles stored in MinIO
- Metadata stored in Postgres

### Verification
- `verify_phase_1.py` confirms ≥10 articles fetched

---

## PHASE 2 – Content Normalization

### Objectives
- Extract clean article text
- Handle HTML and PDF

### Constraints
- PDF extraction ONLY via:
  - `pdfplumber` OR `pypdf`
- No OCR
- No system-level dependencies

### Output
- Clean text field populated
- Word count stored

### Verification
- `verify_phase_2.py` validates non-empty content

---

## PHASE 3 – Language Detection

### Objectives
- Detect Bangla vs English

### Implementation Notes
- Use fastText `lid.176.bin`
- Create `scripts/download_models.py`
- Model file stored in `./models/`
- Model NOT committed to git

### Output
- language field
- confidence score

### Verification
- `verify_phase_3.py` checks mixed-language accuracy

---

## PHASE 4 – Categorization (Baseline)

### Objectives
- Assign topics using heuristic baseline

### Topics
- Politics
- Economy
- Health
- Education
- Technology
- Climate
- Crime
- Religion
- Culture
- Sports

### Constraints
- Keyword + rules only
- No ML training yet

### Output
- Topic + confidence

### Verification
- `verify_phase_4.py`

---

## PHASE 5 – Entity Extraction (Rule-Based)

### Objectives
- Extract entities using:
  - Regex
  - Gazetteer lists

### Entities
- Person
- Organization
- Location
- Date

### Output
- Entity table populated
- Article-entity mapping

### Verification
- `verify_phase_5.py`

---

## PHASE 6 – Summarization (API / Mock)

### Objectives
- Generate:
  - Short summary
  - Bullet points

### Constraints
- Use API-based summarization OR mock summarizer
- Must be swappable later

### Output
- summary_short
- summary_bullets

### Verification
- `verify_phase_6.py`

---

## PHASE 7 – Embeddings & Semantic Search (OPTIONAL MVP+)

### Objectives
- Generate embeddings
- Enable semantic search

### Constraints
- Default: API embeddings
- Qdrant enabled only after system stability

---

## PHASE 8 – API Layer

### Endpoints
- `/articles`
- `/search`
- `/topics/{name}`
- `/entities/{name}`

---

## PHASE 9 – Continuous Execution

- Celery beat
- Retry logic
- Priority scheduling

---

## 6. Success Criteria

- Pipeline runs end-to-end
- Restart-safe
- Verified phase-by-phase
- Understandable by human engineer in <30 minutes

---

## 7. Forbidden Actions

- No monolithic files
- No silent failures
- No skipping verification scripts


⸻