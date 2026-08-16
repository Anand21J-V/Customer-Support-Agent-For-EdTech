# Student Support AI

Student-only agentic support layer for EdTech platforms.

## Phase 0 — Bootstrap

Minimal FastAPI skeleton with configuration loading and a health endpoint.

### Prerequisites

- Python 3.11+
- Local MySQL Server (MySQL Workbench is the GUI client)

### Setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment template:

```bash
copy .env.example .env
```

On Linux/macOS use `cp .env.example .env`.

### Run Phase 0 tests

```bash
pytest tests/unit/test_health.py -q
```

`pytest.ini` sets the project root on `PYTHONPATH` so local `app` imports resolve correctly.

### Run the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
```

---

## Phase 1 — MySQL Foundation (Local Workbench + Raw SQL)

This phase uses **local MySQL Server** and **MySQL Workbench**. Do **not** use Docker MySQL for Phase 1.

Python talks to MySQL with **raw SQL** via `mysql-connector-python` (no ORM).

### Step 1: MySQL Workbench setup

1. Open MySQL Workbench and connect to `localhost:3306` as **root** (or admin).
2. Run these SQL files in order:
   - [`app/db/schema/00_create_database_and_user.sql`](app/db/schema/00_create_database_and_user.sql)
   - [`app/db/schema/01_schema.sql`](app/db/schema/01_schema.sql)
   - [`app/db/schema/02_seed.sql`](app/db/schema/02_seed.sql)
3. In `00_create_database_and_user.sql`, change `'changeme'` to your chosen password.
4. Put the same password in your local `.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=student_support
MYSQL_USER=student_ai
MYSQL_PASSWORD=your_password_here
```

5. Verify in Workbench:

```sql
USE student_support;
SELECT external_id, name FROM students;
```

You should see `stu_A` through `stu_E`.

### Seed scenarios (deterministic test data)

| Student | Scenario |
|---------|----------|
| `stu_A` | payment success, enrollment active, certificate issued |
| `stu_B` | payment success, enrollment pending |
| `stu_C` | payment success, enrollment active, certificate missing |
| `stu_D` | payment failed, enrollment pending |
| `stu_E` | duplicate success payments |

### Step 2: Run Phase 1 tests

```bash
pytest tests/integration/test_mysql_repos.py -q
```

If MySQL is not running or `.env` is missing the password, tests fail with a clear setup message.

### Optional: re-seed from Python

After Workbench setup, you can re-run the seed file:

```bash
python scripts/seed_mysql.py
```

### Repository functions (raw SQL)

- `get_student(external_id)`
- `get_student_by_id(id)`
- `get_course_by_external_id(external_id)`
- `get_enrollment(student_id, course_id)`
- `get_payment(transaction_id)`
- `get_payments_by_student_course(student_id, course_id)`
- `get_certificate(student_id, course_id)`
- `get_assignment(assignment_id)`
- `get_submission(assignment_id, student_id)`

---

## Project structure (Phase 1)

```text
app/
  main.py
  config.py
  api/
    health.py
  db/
    mysql.py
    schema/
      00_create_database_and_user.sql
      01_schema.sql
      02_seed.sql
    repositories/
      student.py
      enrollment.py
      payment.py
      certificate.py
      assignment.py
scripts/
  seed_mysql.py
tests/
  unit/
    test_health.py
  integration/
    test_mysql_repos.py
.env.example
requirements.txt
docker-compose.yml
```

### Docker note

`docker-compose.yml` still defines MySQL/Redis/Qdrant for later phases. For Phase 1, use **local MySQL only**.

---

## Phase 2 — Qdrant Foundation (Open Source)

This phase adds hybrid knowledge retrieval using:

- **Qdrant** (Docker) for vector search
- **sentence-transformers** (`BAAI/bge-small-en-v1.5`, 384-dim) for local embeddings
- **rank-bm25** for keyword search

Knowledge source: [`knowledge-base/Student-Policy-knowledge-base.docx`](knowledge-base/Student-Policy-knowledge-base.docx)

Do **not** ingest [`knowledge-base/Student-dataset.csv`](knowledge-base/Student-dataset.csv). That CSV is for router/evaluation in later phases.

No Gemini API key is required for Phase 2.

### Step 1: Start Qdrant

```powershell
docker compose up qdrant -d
curl http://localhost:6333/healthz
```

Dashboard: `http://localhost:6333/dashboard`

Do not start Docker MySQL if you are already using local MySQL on port `3306`.

### Step 2: Configure embedding settings

Ensure your `.env` includes:

```env
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSION=384
KNOWLEDGE_DOCX_PATH=knowledge-base/Student-Policy-knowledge-base.docx
BM25_CACHE_PATH=data/evaluation/bm25_corpus.json
INGEST_MANIFEST_PATH=data/evaluation/ingest_manifest.json
```

The first embedding run downloads the model weights once (~130MB).

### Step 3: Ingest the knowledge base

```powershell
python scripts/ingest_knowledge.py
```

This will:

1. Parse 20 policy sections from the DOCX
2. Create semantic chunks with metadata
3. Embed chunks locally
4. Upsert vectors into Qdrant
5. Write BM25 manifest files under `data/evaluation/`

### Step 4: Run Phase 2 tests

Offline parser/chunking/embedding tests:

```powershell
pytest tests/retrieval/test_docx_parser.py tests/retrieval/test_chunking.py tests/retrieval/test_embeddings.py -q
```

Hybrid retrieval integration tests (requires Qdrant + ingest):

```powershell
pytest tests/retrieval/test_hybrid_search.py -q
```

Exit criteria query:

```text
Can I get my money back after cancelling?
```

Expected: top results include `POL-REFUND-001`.

### Hybrid search API (library only)

```python
from app.retrieval.hybrid import hybrid_search

results = hybrid_search("Can I get my money back after cancelling?")
```

Phase 2 does not add new FastAPI endpoints. Existing `/health` behavior is unchanged.

### Troubleshooting

- **Docker Desktop must be running** before `docker compose up qdrant -d`
- `Could not connect to Qdrant` → start Docker Desktop, then run `docker compose up qdrant -d`
- `Qdrant collection is empty` → run `python scripts/ingest_knowledge.py`
- Slow first run → sentence-transformers is downloading the model
- Reset Qdrant data → `docker compose down` then remove the `qdrant_data` volume if needed

---

## Project structure (Phase 2)

```text
app/
  main.py
  config.py
  api/
    health.py
  db/
    ...
  retrieval/
    docx_parser.py
    chunking.py
    embeddings.py
    qdrant_client.py
    bm25_index.py
    hybrid.py
  schemas/
    knowledge.py
knowledge-base/
  Student-Policy-knowledge-base.docx
  Student-dataset.csv
data/
  evaluation/
scripts/
  seed_mysql.py
  ingest_knowledge.py
tests/
  unit/
  integration/
  retrieval/
docker-compose.yml
```

---

## Next phases

- Phase 3: LLM client integration
- Phase 4+: Intent router, agents, LangGraph orchestration

See `Skill/Students_plan.md` for the full build plan.
