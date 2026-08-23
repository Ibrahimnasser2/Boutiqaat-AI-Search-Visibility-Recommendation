# User Guide

How to run and use the **AI Search Visibility Analyzer** for Boutiqaat.

## Overview

The platform measures **observable AI-search visibility** — whether Boutiqaat is mentioned, recommended, and ranked when customers ask AI-powered search tools about beauty and skincare retail in the GCC.

It does **not** reverse-engineer proprietary ranking algorithms inside ChatGPT, Google, or Perplexity.

## Getting Started

### 1. Start the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

### 2. Run an analysis

Click **Run Full Analysis** on the dashboard. The system will:

- Load the GCC beauty query set from `data/sample_queries.csv`
- Run each query through the configured LLM provider
- Extract recommendations, rankings, competitors, and sources
- Calculate visibility metrics and improvement opportunities

### 3. Review results

**Dashboard**

- Mention rate, recommendation rate, visibility score, top-3 rate
- Visibility breakdown by query intent
- Competitor comparison table
- Prioritized opportunity cards

**Query detail**

Click any run to inspect:

- Full AI-generated answer
- Boutiqaat status (mentioned / recommended / position)
- Competitor list and cited sources
- Suggested actions for weaker visibility

### 4. Export a report

Click **Export Report** to generate:

- `reports/sample_report.html`
- `reports/sample_report.json`
- `reports/sample_report.csv`

Or run from the command line:

```bash
python scripts/seed_demo.py
```

## Key Concepts

**Mentioned vs recommended**

Boutiqaat can appear in an answer without being actively recommended. The analyzer treats these as separate signals.

Example: *"Companies such as Sephora and Boutiqaat are popular"* → mentioned, not recommended.

**Visibility Score**

A weighted composite (0–100) based on mention, recommendation, top-3 placement, and source support. See `README.md` for the exact formula.

**Opportunities**

When visibility is weak, the system surfaces possible explanations using **observed signal** language — correlations, not proven causes.

## Configuration

**Offline mode (default)**

```env
MOCK_MODE=true
```

Uses deterministic responses — no API key required.

**Live OpenAI**

```env
MOCK_MODE=false
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## Testing

```bash
cd backend
pytest -v
```

## Video Walkthrough

A screen recording of the workflow is available at `reports/demo_recording.webm`.

To record a new version:

```bash
# Terminal 1
cd backend && uvicorn app.main:app --port 8000

# Terminal 2
python scripts/record_demo.py
```
