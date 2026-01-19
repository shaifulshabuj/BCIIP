PROMPTS.md

This is what you actually paste into GitHub Copilot / Cursor / Windsurf, step by step.

# GitHub Copilot Agent Prompts – BCIIP

---

## PROMPT 0 – Phase 0 Initialization

Read PROJECT_SPEC.md carefully.

We are starting Phase 0 only.

Tasks:
1. Initialize repository structure
2. Setup Poetry with Python 3.11
3. Create Dockerfile and docker-compose.yml
4. Add PostgreSQL, Redis, MinIO services
5. Create FastAPI skeleton
6. Add verify_phase_0.py to confirm connectivity

Rules:
- Do NOT start Phase 1
- Ensure `docker-compose up --build` succeeds
- Document assumptions in README

Stop when Phase 0 verification passes.

---

## PROMPT 1 – Phase 1 Crawling

Phase 0 is verified.

Execute Phase 1 only.

Tasks:
1. Implement RSS-based crawling
2. Add initial Bangladesh sources
3. Store raw content in MinIO
4. Store metadata in Postgres
5. Add verify_phase_1.py

Rules:
- Respect robots.txt
- Log crawl results
- Do NOT normalize content yet

Stop after verification script passes.

---

## PROMPT 2 – Phase 2 Normalization

Phase 1 verified.

Execute Phase 2 only.

Tasks:
1. Extract clean text from HTML
2. Extract text from PDFs using pdfplumber or pypdf
3. Store clean text + word count
4. Add verify_phase_2.py

Rules:
- No OCR
- No new system dependencies

---

## PROMPT 3 – Phase 3 Language Detection

Phase 2 verified.

Tasks:
1. Implement fastText language detection
2. Add download_models.py
3. Detect Bangla vs English
4. Store confidence score
5. Add verify_phase_3.py

Rules:
- Do NOT commit model files
- Fail gracefully if model missing

---

## PROMPT 4 – Phase 4 Categorization

Phase 3 verified.

Tasks:
1. Implement rule-based topic categorization
2. Store topic confidence
3. Add verify_phase_4.py

---

## PROMPT 5 – Phase 5 Entity Extraction

Phase 4 verified.

Tasks:
1. Implement regex-based entity extraction
2. Create entity tables
3. Add verify_phase_5.py

---

## PROMPT 6 – Phase 6 Summarization

Phase 5 verified.

Tasks:
1. Implement summarization via API or mock
2. Ensure swappable design
3. Add verify_phase_6.py

---

## PROMPT 7 – Phase 7 Embeddings (Optional)

Only proceed if system is stable.

---

## PROMPT 8 – API Layer

Expose APIs after pipeline is stable.

---

## PROMPT 9 – Continuous Execution

Add Celery scheduling and retries.

---

## PROMPT 10 – Final Review

- Clean code
- Update README
- Document architecture