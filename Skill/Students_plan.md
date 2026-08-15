# Student Support AI Layer — Full Build Plan

## 0. Project Goal

Build a **Student-only Agentic AI Support Layer** for a large EdTech platform.

The system must be able to:

1. Understand what a student is asking.
2. Decide whether the query needs:
   - knowledge retrieval,
   - a backend/tool lookup,
   - learning assistance,
   - multiple steps,
   - or human escalation.
3. Retrieve grounded information from a vector database.
4. Call controlled business tools.
5. Combine evidence from retrieval and tools.
6. Verify the proposed answer.
7. Return a grounded answer or escalate.
8. Be measurable and testable at every stage.

The initial implementation is intentionally limited to **Student Support**. Tutor support will be added later without redesigning the core orchestration model.

---

# 1. Core Architecture

```text
                         STUDENT
                            |
                            v
                  +-------------------+
                  |  Chat/API Input   |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  | Context Manager   |
                  | user/session/msg  |
                  +---------+---------+
                            |
                            v
                +-----------------------+
                |   LangGraph           |
                |   Orchestrator        |
                +-----------+-----------+
                            |
                            v
                  +-------------------+
                  |   Intent Router    |
                  +---------+---------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
      +---------------+ +-----------+ +-----------+
      | Knowledge     | |Operations | | Learning  |
      | Agent         | |Agent      | | Agent     |
      +-------+-------+ +-----+-----+ +-----+-----+
              |               |             |
              v               v             v
          Qdrant          Tool Registry   Course KB
              |               |             |
              +---------------+-------------+
                              |
                              v
                    +--------------------+
                    | Verification Layer |
                    +----------+---------+
                               |
                      +--------+--------+
                      |                 |
                      v                 v
                +-----------+     +-----------+
                | Response  |     | Escalation|
                | Agent     |     | Agent     |
                +-----------+     +-----------+
```

---

# 2. Technology Stack

## Core

- Python 3.11+
- FastAPI
- LangGraph
- Pydantic
- Google Gemini API
- Qdrant
- MySQL
- Redis
- Docker / Docker Compose

## AI / Retrieval

- Gemini 3.6 Flash for the primary LLM
- Gemini 3.5 Flash-Lite where a cheaper/faster model is sufficient
- Gemini Embedding 2 for embeddings
- BM25 / keyword retrieval
- Vector similarity search
- Metadata filtering
- Reranking

Google currently lists Gemini 3.6 Flash as a stable production model for agentic workloads and Gemini 3.5 Flash-Lite as a lower-cost high-throughput option. Google also lists `gemini-embedding-2` as its current stable embedding model. Use model IDs through configuration rather than hardcoding them throughout the codebase. [Google Gemini Models](https://ai.google.dev/gemini-api/docs/models)

## Observability / Evaluation

- LangSmith
- OpenTelemetry
- DeepEval
- Python logging

---

# 3. Current Project Scope

### Included in V1

- Student-only support
- Query understanding
- Intent routing
- Knowledge retrieval
- Tool routing
- Multi-step planning
- Verification
- Response generation
- Escalation decision
- Evaluation
- MySQL
- Qdrant

### Explicitly excluded from V1

- Tutor support
- Voice support
- WhatsApp integration
- Full CRM integration
- Payment gateway implementation
- Production Kubernetes
- Fine-tuning the LLM
- Autonomous unrestricted web browsing

---

# 4. Student Intent Taxonomy

Initial intents:

```text
course_access
enrollment
payment
refund
certificate
assignment
exam
technical_issue
account
course_information
schedule
tutor_support
progress
attendance
subscription
academic_question
course_content
feedback_complaint
human_support
unknown
```

This list is the initial routing taxonomy, not a permanent contract.

The router must be designed so new intents can be added through configuration/schema updates without rewriting the complete graph.

---

# 5. Dataset

Current dataset:

```text
student_edtech_support_5000_with_responses.csv
```

It contains:

```text
query_id
user_type
intent
category
query
response
requires_rag
requires_tool
requires_escalation
priority
```

The dataset is used for:

- Intent-router evaluation
- Routing evaluation
- Tool-need evaluation
- Escalation evaluation
- Response evaluation
- Regression tests

## Important

Do **not** treat this CSV as the actual platform knowledge base.

The responsibilities are different:

```text
CSV
 |
 +--> Router/evaluation examples

Qdrant
 |
 +--> Actual support knowledge and course documents

MySQL
 |
 +--> Actual student/business state
```

---

# 6. Repository Structure

Recommended structure:

```text
student-support-ai/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── chat.py
│   │   └── health.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── builder.py
│   │   ├── nodes/
│   │   │   ├── context.py
│   │   │   ├── router.py
│   │   │   ├── planner.py
│   │   │   ├── knowledge.py
│   │   │   ├── operations.py
│   │   │   ├── learning.py
│   │   │   ├── verification.py
│   │   │   ├── response.py
│   │   │   └── escalation.py
│   │   └── edges.py
│   │
│   ├── agents/
│   │   ├── router_agent.py
│   │   ├── knowledge_agent.py
│   │   ├── operations_agent.py
│   │   ├── learning_agent.py
│   │   ├── verification_agent.py
│   │   └── escalation_agent.py
│   │
│   ├── llm/
│   │   ├── client.py
│   │   ├── models.py
│   │   └── prompts.py
│   │
│   ├── retrieval/
│   │   ├── embeddings.py
│   │   ├── chunking.py
│   │   ├── qdrant_client.py
│   │   ├── bm25.py
│   │   ├── hybrid.py
│   │   └── reranker.py
│   │
│   ├── tools/
│   │   ├── registry.py
│   │   ├── student.py
│   │   ├── enrollment.py
│   │   ├── payment.py
│   │   ├── assignment.py
│   │   ├── certificate.py
│   │   ├── course.py
│   │   └── support.py
│   │
│   ├── db/
│   │   ├── mysql.py
│   │   ├── queries/
│   │   └── schema/
│   │
│   ├── memory/
│   │   ├── redis.py
│   │   └── context.py
│   │
│   ├── schemas/
│   │   ├── router.py
│   │   ├── tools.py
│   │   └── responses.py
│   │
│   └── utils/
│
├── data/
│   ├── datasets/
│   │   └── student_edtech_support_5000_with_responses.csv
│   ├── knowledge/
│   └── evaluation/
│
├── scripts/
│   ├── init_mysql.py
│   ├── seed_mysql.py
│   ├── ingest_knowledge.py
│   ├── evaluate_router.py
│   ├── evaluate_rag.py
│   └── evaluate_end_to_end.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── graph/
│   ├── retrieval/
│   └── evaluation/
│
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

# 7. Environment Setup

## Python

Use Python 3.11+.

Create a virtual environment:

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

Install:

```bash
pip install -r requirements.txt
```

Minimum package groups:

```text
fastapi
uvicorn
langgraph
langchain
langchain-google-genai
google-genai
qdrant-client
mysql-connector-python
redis
pydantic
python-dotenv
pandas
rank-bm25
httpx
pytest
deepeval
```

Use the Google GenAI SDK for direct Gemini API access. Google's current API documentation recommends the official `google-genai` SDK and documents agentic use through the Gemini API. [Gemini API](https://ai.google.dev/gemini-api/docs)

---

# 8. Environment Variables

Create:

```text
.env
```

Example:

```env
GEMINI_API_KEY=

GEMINI_GENERATION_MODEL=gemini-3.6-flash
GEMINI_FAST_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-2

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=student_support
MYSQL_USER=student_ai
MYSQL_PASSWORD=

REDIS_HOST=localhost
REDIS_PORT=6379

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=student_support_knowledge

TOP_K_VECTOR=10
TOP_K_BM25=10
TOP_K_FINAL=5

LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=student-support-ai

LOG_LEVEL=INFO
```

Never commit `.env`.

---

# 9. Docker Infrastructure

For local development use Docker Compose.

Services:

```text
mysql
redis
qdrant
```

Do not add Kafka/Kubernetes yet.

Initial Docker architecture:

```text
+--------------------+
| FastAPI / AI App   |
+---------+----------+
          |
   +------+-------+----------------+
   |              |                |
   v              v                v
 MySQL           Redis           Qdrant
```

---

# 10. MySQL Setup

## 10.1 Create database

```sql
CREATE DATABASE student_support
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Create a restricted application user:

```sql
CREATE USER 'student_ai'@'%' IDENTIFIED BY 'CHANGE_ME';

GRANT SELECT, INSERT, UPDATE
ON student_support.*
TO 'student_ai'@'%';

FLUSH PRIVILEGES;
```

Do not use the root account from the application.

---

# 11. MySQL Schema

Create these tables first:

```sql
CREATE TABLE students (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);
```

```sql
CREATE TABLE courses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(64) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
CREATE TABLE enrollments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    status VARCHAR(32) NOT NULL,
    enrolled_at DATETIME,
    completed_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id) REFERENCES students(id),

    CONSTRAINT fk_enrollment_course
        FOREIGN KEY (course_id) REFERENCES courses(id),

    UNIQUE KEY uq_student_course (student_id, course_id)
);
```

```sql
CREATE TABLE payments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    course_id BIGINT,
    transaction_id VARCHAR(128) NOT NULL UNIQUE,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

```sql
CREATE TABLE assignments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    course_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

```sql
CREATE TABLE submissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    assignment_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    status VARCHAR(32) NOT NULL,
    submitted_at DATETIME,
    grade DECIMAL(5,2),

    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

```sql
CREATE TABLE certificates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    status VARCHAR(32) NOT NULL,
    certificate_url TEXT,
    issued_at DATETIME,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

```sql
CREATE TABLE support_tickets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    conversation_id VARCHAR(128),
    intent VARCHAR(128),
    priority VARCHAR(32),
    status VARCHAR(32) NOT NULL DEFAULT 'open',
    summary TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,

    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

---

# 12. MySQL Seed Data

Create realistic mock data.

Minimum initial seed:

```text
100 students
20 courses
500 enrollments
500-1000 payments
100 assignments
1000 submissions
100 certificates
```

The objective is not realism at production scale. The objective is enough data to test tools.

Seed scenarios deliberately:

```text
student A:
payment=success
enrollment=active
access=active

student B:
payment=success
enrollment=pending

student C:
payment=success
enrollment=active
certificate=missing

student D:
payment=failed

student E:
duplicate payments
```

These become deterministic test cases.

---

# 13. AI Tool Layer

Tools should expose business capabilities, not raw SQL.

Example:

```python
get_payment_status(student_id, course_id)
get_enrollment_status(student_id, course_id)
get_course_progress(student_id, course_id)
get_certificate_status(student_id, course_id)
get_assignment_status(student_id, assignment_id)
get_course_schedule(student_id, course_id)
create_support_ticket(student_id, conversation_id, ...)
```

Every tool must:

1. Validate arguments.
2. Validate authorization.
3. Query the database/service.
4. Return structured JSON.
5. Never return unnecessary PII.

---

# 14. Tool Output Contract

Example:

```json
{
  "success": true,
  "tool": "get_payment_status",
  "data": {
    "status": "success",
    "transaction_id": "TXN123",
    "amount": 4999,
    "currency": "INR"
  }
}
```

Failure:

```json
{
  "success": false,
  "tool": "get_payment_status",
  "error_code": "PAYMENT_NOT_FOUND",
  "message": "No payment matched the supplied student and course."
}
```

Use Pydantic models for these contracts.

---

# 15. Qdrant Setup

Run Qdrant locally with Docker.

Default:

```text
http://localhost:6333
```

Create one collection initially:

```text
student_support_knowledge
```

Do not create 20 collections for 20 intents.

Use metadata filtering.

---

# 16. Embedding Model

Use Google's current stable:

```text
gemini-embedding-2
```

Google documents this model as its current multimodal embedding model with configurable output dimensions from 128 to 3072; for a text-only support system, choose one dimension and keep it fixed for the collection. [Gemini Embedding 2](https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2)

Recommended initial configuration:

```env
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSION=768
```

Do not change embedding dimensions after indexing without recreating/reindexing the collection.

Google's older `gemini-embedding-001` was deprecated in July 2026 and Google recommends `gemini-embedding-2`; do not start this project on old embedding model IDs. [Google deprecations](https://ai.google.dev/gemini-api/docs/deprecations)

---

# 17. Knowledge Base

For V1 create a controlled knowledge corpus.

Suggested documents:

```text
knowledge/
├── refund_policy.md
├── enrollment_policy.md
├── certificate_policy.md
├── assignment_policy.md
├── exam_policy.md
├── course_access_guide.md
├── account_help.md
├── payment_help.md
├── technical_support.md
├── attendance_policy.md
├── subscription_policy.md
├── student_handbook.md
└── course_catalog.md
```

Later replace these with real platform documents.

---

# 18. Document Ingestion Pipeline

```text
Documents
   |
   v
Parse
   |
   v
Clean
   |
   v
Chunk
   |
   v
Metadata
   |
   v
Gemini Embedding 2
   |
   v
Qdrant
```

---

# 19. Chunking Strategy

Do not blindly chunk every document into arbitrary token blocks.

Prefer semantic sections.

Example:

```text
Refund Policy
  |
  +-- Eligibility
  +-- Exclusions
  +-- Request process
  +-- Processing time
  +-- Exceptions
```

Recommended initial chunk parameters:

```text
target chunk size: 400-800 tokens
overlap: 50-100 tokens
```

Adjust based on retrieval evaluation.

Every chunk must store:

```json
{
  "document_id": "refund_policy",
  "section": "eligibility",
  "title": "Refund Policy",
  "category": "refund",
  "audience": "student",
  "version": 1,
  "status": "active"
}
```

---

# 20. Qdrant Payload

Use payload filtering.

Example:

```json
{
  "document_id": "refund_policy_v1",
  "category": "refund",
  "audience": "student",
  "status": "active",
  "version": 1
}
```

The retriever should prefer:

```text
audience = student
status = active
```

---

# 21. Hybrid Retrieval

Implement retrieval in stages.

### Stage 1

BM25 retrieval.

### Stage 2

Vector retrieval.

### Stage 3

Merge candidates.

### Stage 4

Metadata filtering.

### Stage 5

Reranking.

### Stage 6

Return top evidence.

```text
Query
 |
 +--> BM25 ----+
 |             |
 +--> Vector --+--> Merge --> Filter --> Rerank --> Top-K
```

Initial values:

```env
BM25_TOP_K=10
VECTOR_TOP_K=10
FINAL_TOP_K=5
```

Do not assume these numbers are optimal. Measure them.

---

# 22. Query Rewriting

Before retrieval, the Knowledge Agent may rewrite the query.

Example:

```text
Student:
"Can I get my money back if I stop the course?"
```

Rewrite:

```text
"Student refund eligibility for course cancellation"
```

The rewritten query should preserve the original meaning.

Use the query rewrite only for search; retain the original student message for the final answer.

---

# 23. Intent Router Output Schema

The router should produce strict structured output:

```json
{
  "intent": "refund",
  "sub_intent": "refund_eligibility",
  "route": "knowledge",
  "requires_rag": true,
  "requires_tool": false,
  "requires_planning": false,
  "escalation_candidate": false,
  "confidence": 0.92
}
```

The application should validate this with Pydantic.

If parsing fails:

```text
retry once with constrained output
```

If it still fails:

```text
fallback classification
```

Do not continue with malformed router state.

---

# 24. Agent Routing Rules

Initial routing:

```text
course_information   -> knowledge
refund               -> knowledge / operations
payment              -> operations
enrollment           -> operations
course_access        -> operations
certificate          -> operations
assignment           -> operations / knowledge
exam                 -> knowledge / operations
technical_issue      -> operations / knowledge
account              -> operations
schedule              -> operations
progress              -> operations
attendance            -> operations
subscription         -> operations
academic_question    -> learning
course_content       -> knowledge / learning
tutor_support        -> operations / escalation
feedback_complaint   -> escalation check
human_support        -> escalation
unknown               -> knowledge search -> clarify/escalate
```

These are defaults, not immutable rules.

---

# 25. Planner

Use the planner only when more than one step is necessary.

Example:

```text
"I paid yesterday but I'm not enrolled."
```

Plan:

```text
1. get_payment_status
2. get_enrollment_status
3. compare
4. diagnose
5. take allowed action if available
6. verify
```

Avoid planning for:

```text
"What is your refund policy?"
```

A simple query should remain cheap.

---

# 26. Verification Design

Verification receives:

```text
original user query
router output
retrieved evidence
tool results
draft response
```

Verify:

### Grounding

Is the answer supported by actual evidence?

### Tool consistency

Does the answer match tool results?

### Policy consistency

Does it contradict known policy?

### Scope

Is the answer answering the actual question?

### Safety

Could the response cause harm or make an unauthorized business claim?

---

# 27. Verification Output

```json
{
  "verified": true,
  "grounding_score": 0.94,
  "policy_valid": true,
  "tool_consistent": true,
  "safe": true,
  "reason": null
}
```

Failure example:

```json
{
  "verified": false,
  "grounding_score": 0.31,
  "policy_valid": false,
  "tool_consistent": true,
  "safe": true,
  "reason": "Draft response states a refund timeframe not supported by current policy."
}
```

---

# 28. Response Generation

Response Agent receives only verified context.

Use a strict system instruction:

```text
Answer using verified evidence only.
Do not invent policies, prices, dates, account states, or actions.
Do not claim an action succeeded unless a tool result confirms it.
When evidence is insufficient, say so and route to the appropriate next step.
```

The final response should be:

- clear,
- concise,
- student-friendly,
- explicit about actions,
- explicit about uncertainty.

---

# 29. Escalation Logic

Escalate when:

```text
student explicitly requests human
OR
high-risk financial issue
OR
policy exception required
OR
no reliable answer exists
OR
tool failure persists
OR
verification fails repeatedly
OR
case requires manual judgment
```

Do not escalate every unknown question.

Preferred flow:

```text
Unknown
  |
  v
Try safe clarification
  |
  v
Can it be resolved?
  |
 +----+
 |    |
YES   NO
 |    |
 v    v
Solve Escalate
```

---

# 30. Conversation Memory

V1:

```text
Short-term conversation memory
```

Store:

```text
conversation_id
messages
current intent
entities
current plan
tool results
last response
```

Redis is appropriate for fast state.

Do not create long-term semantic memory yet.

---

# 31. LLM Strategy

Use Google models through configuration.

### Primary reasoning model

```text
gemini-3.6-flash
```

Use for:

- planning,
- complex routing,
- verification,
- final answer generation.

### High-throughput model

```text
gemini-3.5-flash-lite
```

Use for:

- cheap classification,
- simple query transformations,
- high-volume lightweight work.

Google currently identifies Gemini 3.6 Flash as a stable model suited to agentic workloads and Gemini 3.5 Flash-Lite as the lower-cost high-throughput model. [Google latest Gemini models](https://ai.google.dev/gemini-api/docs/latest-model)

Keep all model IDs in `.env` so the system can migrate without code changes.

---

# 32. LLM Call Budget

Do not let every request invoke every agent.

### Simple FAQ

Target:

```text
1 router call
1 retrieval operation
1 response call
1 verification call
```

### Simple tool query

Target:

```text
1 router
1 tool
1 response
1 verification
```

### Complex query

Allow:

```text
1 router
1 planner
N tools
1 verification
1 response
```

Add strict maximums:

```env
MAX_TOOL_CALLS=5
MAX_GRAPH_STEPS=12
MAX_REPLAN_ATTEMPTS=1
```

This prevents runaway agent loops.

---

# 33. Model Failure Handling

Every LLM call must handle:

```text
timeout
rate limit
invalid JSON
empty response
safety refusal
API error
```

Fallback policy:

```text
retry once
   |
   v
still failing
   |
   v
safe fallback
   |
   +--> clarification
   |
   +--> escalation
```

Never fabricate a successful result after an LLM/API failure.

---

# 34. Testing Strategy

Testing is mandatory phase by phase.

## Unit Tests

Test:

- Pydantic schemas
- router parser
- chunker
- metadata
- tool validation
- DB queries
- Qdrant adapter
- Redis adapter

## Integration Tests

Test:

```text
Router -> Knowledge
Router -> Operations
Router -> Learning
Tool -> MySQL
Embedding -> Qdrant
Graph -> Verification
```

## End-to-End Tests

Test real student journeys.

---

# 35. Golden Test Set

From your 5,000-row dataset, create a smaller fixed regression set:

```text
500 queries
```

Target distribution:

```text
25 per intent
```

Run it on every major change.

Measure:

```text
intent_accuracy
route_accuracy
rag_required_accuracy
tool_required_accuracy
escalation_accuracy
```

---

# 36. RAG Evaluation

Create a separate evaluation dataset containing:

```text
question
expected_document
expected_section
expected_answer_facts
```

Metrics:

```text
Recall@K
Precision@K
MRR
nDCG
Groundedness
Answer correctness
```

A retrieval system that gives fluent but irrelevant documents is a failure.

---

# 37. Tool Evaluation

Create tests like:

```text
Input:
"I paid for DS101 yesterday but cannot access it."

Expected:
get_payment_status
get_enrollment_status
get_course_access
```

Measure:

```text
correct_tool_selection
correct_arguments
correct_order
successful_execution
```

---

# 38. Escalation Evaluation

Create test examples for:

```text
clear resolvable case
ambiguous case
high-risk case
policy exception
unknown case
failed tool case
human-request case
```

Measure:

```text
Escalation Precision
Escalation Recall
Unsafe Non-Escalation Rate
Unnecessary Escalation Rate
```

The most important failure:

> The system should not confidently answer a question it should have escalated.

---

# 39. End-to-End Test Scenarios

Minimum V1 scenarios:

### Scenario 1 — FAQ

```text
"What is the refund policy?"
```

Expected:

```text
Knowledge Agent
```

### Scenario 2 — Payment

```text
"My payment failed."
```

Expected:

```text
Operations Agent
```

### Scenario 3 — Payment + enrollment

```text
"I was charged but the course is still locked."
```

Expected:

```text
Planner
-> payment
-> enrollment/access
-> diagnosis
```

### Scenario 4 — Academic

```text
"Explain gradient descent."
```

Expected:

```text
Learning Agent
```

### Scenario 5 — Unknown

```text
"Can I transfer my course to my brother?"
```

Expected:

```text
Knowledge check
-> insufficient evidence
-> clarify/escalate
```

### Scenario 6 — Human

```text
"I want to speak to a human."
```

Expected:

```text
Escalation
```

---

# 40. Phase-Wise Implementation Plan

## Phase 0 — Project Bootstrap

### Goal

Working development environment.

### Tasks

- Create repository
- Create Python environment
- Install dependencies
- Create `.env`
- Add config loader
- Create FastAPI skeleton
- Add health endpoint
- Add Docker Compose

### Exit Criteria

```text
GET /health
```

returns healthy.

---

# Phase 1 — MySQL Foundation

### Goal

Working relational data layer.

### Tasks

1. Start MySQL.
2. Create database.
3. Create tables.
4. Create restricted DB user.
5. Add indexes.
6. Seed students/courses/enrollments/payments.
7. Implement raw SQL repository functions.
8. Test every repository function.

### Exit Criteria

You can execute:

```text
get_student()
get_enrollment()
get_payment()
get_certificate()
get_assignment()
```

and receive deterministic results.

---

# Phase 2 — Qdrant Foundation

### Goal

Working semantic knowledge retrieval.

### Tasks

1. Start Qdrant.
2. Create collection.
3. Create knowledge documents.
4. Chunk documents.
5. Generate Gemini embeddings.
6. Upsert vectors.
7. Add metadata.
8. Implement vector search.
9. Implement BM25.
10. Implement hybrid retrieval.

### Exit Criteria

A query such as:

```text
"Can I get my money back after cancelling?"
```

returns the correct refund-policy chunks.

---

# Phase 3 — Gemini Integration

### Goal

Reliable Google LLM layer.

### Tasks

1. Configure Gemini API.
2. Implement a single reusable client.
3. Add model configuration.
4. Add timeouts.
5. Add retries.
6. Add structured output.
7. Add token logging.
8. Add error handling.

### Exit Criteria

A simple Python test successfully calls:

```text
gemini-3.6-flash
```

and returns validated structured output.

Use current official Google SDK/API documentation rather than copying old examples. Google's API documentation recommends the official `google-genai` SDK and documents both the standard generation API and the Interactions API. [Gemini API documentation](https://ai.google.dev/gemini-api/docs)

---

# Phase 4 — Intent Router

### Goal

Accurately classify student queries.

### Tasks

1. Load 5,000-row dataset.
2. Inspect label distribution.
3. Build Pydantic router schema.
4. Create router prompt.
5. Run predictions on validation data.
6. Measure intent accuracy.
7. Add confidence handling.
8. Add unknown handling.
9. Freeze a 500-case regression set.

### Exit Criteria

Router meets your chosen threshold.

Initial target:

```text
>= 90% intent accuracy
```

Do not optimize for the threshold blindly. Inspect confusion pairs.

---

# Phase 5 — Knowledge Agent

### Goal

Turn queries into grounded answers.

### Tasks

1. Implement query rewriting.
2. Implement hybrid search.
3. Add reranking.
4. Return evidence objects.
5. Build context formatter.
6. Build grounded response prompt.
7. Add citation/source references internally.
8. Test hallucination traps.

### Exit Criteria

The agent answers correctly when the answer exists and refuses/escales when it does not.

---

# Phase 6 — Operations Agent

### Goal

Use actual student data.

### Tasks

1. Implement tool registry.
2. Implement Pydantic tool schemas.
3. Connect tools to MySQL repositories.
4. Add authorization checks.
5. Add tool error handling.
6. Add max-tool-call guard.
7. Test tool selection.
8. Test argument generation.

### Exit Criteria

Example:

```text
"Why isn't my course active?"
```

produces the correct sequence of tool calls.

---

# Phase 7 — Learning Agent

### Goal

Handle academic questions.

### Tasks

1. Detect academic intent.
2. Retrieve relevant course content.
3. Generate explanation.
4. Keep answer aligned to retrieved material.
5. Add hint/example mode.
6. Test unsupported academic questions.

### Exit Criteria

Academic questions route to Learning and not Operations.

---

# Phase 8 — LangGraph Orchestrator

### Goal

Connect all agents into one stateful workflow.

### Tasks

Implement:

```text
load_context
   ↓
intent_router
   ↓
route
   ├── knowledge
   ├── operations
   ├── learning
   └── unknown
   ↓
verification
   ↓
response / escalation
```

Add:

```text
conditional edges
retry
max steps
max tool calls
state validation
```

### Exit Criteria

End-to-end tests pass.

---

# Phase 9 — Verification

### Goal

Prevent unsupported answers.

### Tasks

1. Build verification schema.
2. Add grounding check.
3. Add tool consistency check.
4. Add policy check.
5. Add safety check.
6. Add retry/replan.
7. Add escalation fallback.

### Exit Criteria

Known hallucination traps are rejected.

---

# Phase 10 — Escalation

### Goal

Handle unresolved cases correctly.

### Tasks

1. Build escalation rules.
2. Build escalation agent.
3. Generate structured ticket.
4. Store support ticket in MySQL.
5. Add priority.
6. Test unnecessary and necessary escalation.

### Exit Criteria

High-risk and unsupported cases are not incorrectly answered.

---

# Phase 11 — Redis Conversation Memory

### Goal

Support multi-turn conversations.

Example:

```text
Student:
"I paid for the course."

Bot:
"Which course?"

Student:
"Data Science."

Bot:
...
```

The second turn must understand the previous context.

### Tasks

- Redis session store
- conversation state
- message history
- context compression when required
- expiration policy

### Exit Criteria

Multi-turn tests work without leaking unrelated conversations.

---

# Phase 12 — Observability

### Goal

Understand every agent decision.

Track:

```text
request_id
conversation_id
intent
route
retrieval results
tool calls
LLM calls
latency
token usage
verification
escalation
errors
```

### Exit Criteria

Any failed request can be traced end-to-end.

---

# Phase 13 — Evaluation & Regression

Run:

```text
Router evaluation
Retrieval evaluation
Tool evaluation
Verification evaluation
Escalation evaluation
End-to-end evaluation
```

Every important change must run the regression set.

---

# 41. Definition of Done for V1

V1 is complete only when:

- Student context is loaded correctly.
- Router reliably identifies intents.
- Knowledge retrieval returns relevant evidence.
- Tools return deterministic student data.
- Learning queries route correctly.
- Complex queries can execute multiple steps.
- Verification catches unsupported answers.
- Escalation works.
- Multi-turn state works.
- All major components have tests.
- Regression suite passes.
- Failures are observable.

---

# 42. What NOT to build yet

Do not add these just because they sound "enterprise":

```text
Kubernetes
Kafka
20 agents
Multi-agent-to-multi-agent conversations
Fine-tuning
Autonomous web browsing
Long-term memory
Complex event sourcing
Multiple vector databases
Multiple LLM providers
```

First make the core loop reliable:

```text
UNDERSTAND
   ↓
ROUTE
   ↓
RETRIEVE / TOOL / LEARN
   ↓
VERIFY
   ↓
RESPOND / ESCALATE
```

---

# 43. Final V1 AI Architecture

```text
                         STUDENT MESSAGE
                                |
                                v
                       +----------------+
                       | Context Manager|
                       +-------+--------+
                               |
                               v
                    +----------------------+
                    |   LangGraph Graph    |
                    +----------+-----------+
                               |
                               v
                      +------------------+
                      |   Intent Router  |
                      +--------+---------+
                               |
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
       Knowledge Agent   Operations Agent   Learning Agent
             |                 |                 |
             v                 v                 v
       Hybrid RAG          Tool Registry      Course RAG
             |                 |                 |
             v                 v                 v
          Qdrant          MySQL/Services      Qdrant
             |                 |                 |
             +-----------------+-----------------+
                               |
                               v
                      +-------------------+
                      |   Verification    |
                      +---------+---------+
                                |
                     +----------+----------+
                     |                     |
                     v                     v
               Response Agent        Escalation Agent
                     |                     |
                     +----------+----------+
                                |
                                v
                             STUDENT
```

---

# 44. Important architectural principle

The system should never behave like:

```text
Student
   ↓
LLM
   ↓
Answer
```

It should behave like:

```text
Student
   ↓
Context
   ↓
Intent
   ↓
Plan
   ↓
Evidence / Tools
   ↓
Verification
   ↓
Resolution
      OR
Escalation
```

That is the AI system we will build phase by phase.

---

# 45. External References

Use Google's current official documentation for model/API details:

- Gemini API: https://ai.google.dev/gemini-api/docs
- Models: https://ai.google.dev/gemini-api/docs/models
- Latest models: https://ai.google.dev/gemini-api/docs/latest-model
- Embeddings: https://ai.google.dev/gemini-api/docs/embeddings
- Gemini Embedding 2: https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2
- Deprecations: https://ai.google.dev/gemini-api/docs/deprecations
- API reference: https://ai.google.dev/api

Model selection in this plan is based on Google's current model documentation as of August 2026. The embedding section uses `gemini-embedding-2`, which Google currently lists as stable and recommends over older embedding models. [Models](https://ai.google.dev/gemini-api/docs/models) [Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
