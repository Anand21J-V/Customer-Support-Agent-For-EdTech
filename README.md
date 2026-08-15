# Student Support AI

Student-only agentic support layer for EdTech platforms.

## Phase 0 — Bootstrap

This phase provides a minimal FastAPI skeleton with configuration loading and a health endpoint.

### Prerequisites

- Python 3.11+

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

### Run tests

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

Expected response:

```json
{"status": "ok", "service": "student-support-ai"}
```

### Docker infrastructure (Phase 1+)

`docker-compose.yml` defines MySQL, Redis, and Qdrant for later phases. Do not start these services during Phase 0.

When ready for Phase 1/2:

```bash
docker compose up -d
```

## Project structure (Phase 0)

```text
app/
  main.py
  config.py
  api/
    health.py
tests/
  unit/
    test_health.py
.env.example
requirements.txt
docker-compose.yml
```

## Next phases

- Phase 1: MySQL schema, seed data, repository functions
- Phase 2: Qdrant knowledge retrieval
- Phase 3: Gemini client integration
- Phase 4+: Intent router, agents, LangGraph orchestration

See `Skill/Students_plan.md` for the full build plan.
