# AI Search Visibility & Recommendation Analyzer

A platform that measures **observable AI-search visibility** for Boutiqaat under controlled customer queries. It analyzes whether Boutiqaat is mentioned, recommended, ranked against competitors, and supported by sources — then surfaces potential improvement opportunities.

> **Important:** This system does NOT reverse-engineer ChatGPT, Google, or Perplexity ranking algorithms. It measures what AI assistants *say* when asked specific beauty retail questions.

## Problem

Customers increasingly ask AI assistants *"Which companies would you recommend for skincare in the Middle East?"* instead of searching Google. Boutiqaat needs to understand when and why it appears (or doesn't) in those AI-generated answers.

## Solution

This full-stack analyzer:

1. Loads realistic GCC beauty/skincare customer queries
2. Runs them through an LLM provider (mock or OpenAI)
3. Extracts structured recommendations, rankings, and sources
4. Computes visibility metrics and competitor comparisons
5. Generates opportunity signals with clear observation vs. inference language
6. Presents results in a dashboard and exportable reports

## Architecture

```mermaid
flowchart TB
    FE[React Dashboard] --> API[FastAPI]
    API --> QS[Query Service]
    API --> RS[Report Service]
    QS --> LLM[LLM Provider]
    LLM --> Mock[Mock Provider]
    LLM --> OAI[OpenAI Provider]
    QS --> VA[Visibility Analyzer]
    VA --> CA[Competitor Analyzer]
    VA --> SA[Source Analyzer]
    VA --> OA[Opportunity Analyzer]
    VA --> DB[(SQLite)]
    RS --> DB
```

## Methodology

| Step | Approach |
|------|----------|
| Query selection | 34 realistic GCC beauty queries across discovery, transactional, comparison, product-specific, and local intents |
| AI runs | Structured JSON responses via mock (deterministic) or OpenAI |
| Entity detection | Deterministic normalization for Boutiqaat, boutiqaat.com, بوتيكات |
| Recommendation vs mention | Rule-based: "such as" = mention-only; numbered lists + recommend language = recommended |
| Ranking | Position from structured recommendation list only — never invented |
| Metrics | Transparent composite Visibility Score |
| Opportunities | Heuristic signals labeled as "potential reason" / "observed signal" |

## Metrics & Formulas

**Mention Rate** = (queries where Boutiqaat mentioned) / total runs × 100

**Recommendation Rate** = (queries where Boutiqaat recommended) / total runs × 100

**Average Position** = mean rank over runs where Boutiqaat is recommended

**Top-3 Rate** = (recommended runs with position ≤ 3) / total runs × 100

**Source Coverage** = (recommended runs with Boutiqaat-supporting sources) / recommended runs × 100

**Visibility Score** (per run, 0–100):

| Component | Weight |
|-----------|--------|
| Mentioned | 20% |
| Recommended | 40% |
| Top-3 when recommended | 25% |
| Boutiqaat source present | 15% |

Aggregate score = mean of per-run scores. This is a **custom diagnostic metric**, not an industry standard.

## Out of Scope

| Excluded | Why |
|----------|-----|
| Scraping ChatGPT/Perplexity UI | Against ToS; unreliable for production monitoring |
| Reverse-engineering ranking algorithms | Not possible or defensible |
| Custom ML model | Unnecessary complexity at this stage |
| Large SEO crawler | Out of scope; we analyze AI answers not web index |
| Multi-provider in v1 | Mock + OpenAI sufficient; architecture supports extension |
| PDF report generation | HTML + JSON + CSV cover reporting needs |

## Quick Start (Offline Mode — No API Key)

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend (includes built-in dashboard at http://localhost:8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** → Click **Run Full Analysis**.

> A React frontend is also included in `frontend/` (requires Node.js). The built-in dashboard at `:8000` provides the full experience.

### One-Command Seed + Report

```bash
python scripts/seed_demo.py
```

Generates `reports/sample_report.json`, `.csv`, and `.html`.

## Running With OpenAI

```env
MOCK_MODE=false
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Restart backend. Responses will be non-deterministic.

## Testing

```bash
cd backend
pytest -v
```

All tests run without an API key using deterministic logic.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/queries/load-sample` | Load CSV queries |
| POST | `/api/analysis/run-full` | Run full analysis pipeline |
| POST | `/api/runs` | Batch AI runs |
| GET | `/api/analysis/overview` | Dashboard metrics |
| GET | `/api/analysis/competitors` | Competitor aggregates |
| GET | `/api/analysis/opportunities` | Opportunity cards |
| GET | `/api/analysis/runs/{id}` | Query detail |
| GET | `/api/reports/sample` | Generate report |

Full OpenAPI docs: **http://localhost:8000/docs**

## Video Walkthrough

A screen recording of the application workflow is at `reports/demo_recording.webm`.

To record a new version:

```bash
cd backend && uvicorn app.main:app --port 8000
python scripts/record_demo.py
```

See `DEMO.md` for usage instructions.

After running an analysis, typical results include:

- **~74% mention rate**
- **~49% recommendation rate**
- Top competitors: Sephora, Amazon, Noon, iHerb

See `reports/sample_report.html` for a full example.

## Limitations

- LLM nondeterminism (except mock mode)
- Limited 34-query sample set
- Single provider in initial release
- No access to proprietary AI ranking internals
- Source availability varies by provider
- Opportunity signals are correlational, not causal

## Future Work

- Perplexity / Google AI APIs where supported
- Scheduled monitoring and trend charts
- Larger query sets by geography and category
- A/B testing content changes against visibility

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, OpenAI SDK
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts
- **Database:** SQLite

## Project Structure

```
├── backend/app/          # API, services, models
├── frontend/src/         # React dashboard
├── data/sample_queries.csv
├── reports/              # Generated reports
├── scripts/seed_demo.py
├── DEMO.md               # User guide
└── README.md
```
