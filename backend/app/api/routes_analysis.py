import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.db import models
from app.schemas.answer import AIRunResponse, RunBatchRequest
from app.schemas.analysis import AnalyzeRequest
from app.services.query_service import get_run, list_runs, run_batch, run_single_query
from app.services.visibility_analyzer import analyze_run

router = APIRouter(prefix="/api", tags=["runs"])


@router.post("/runs", response_model=list[AIRunResponse])
def create_runs(request: RunBatchRequest, db: Session = Depends(get_db)):
    runs = run_batch(db, request)
    return [_run_response(r) for r in runs]


@router.post("/runs/{query_id}", response_model=AIRunResponse)
def create_run_for_query(query_id: int, provider: str = "mock", db: Session = Depends(get_db)):
    try:
        run = run_single_query(db, query_id, provider)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _run_response(run)


@router.get("/runs", response_model=list[AIRunResponse])
def get_runs(db: Session = Depends(get_db)):
    return [_run_response(r) for r in list_runs(db)]


@router.get("/runs/{run_id}", response_model=AIRunResponse)
def get_run_by_id(run_id: int, db: Session = Depends(get_db)):
    run = get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_response(run)


@router.post("/analyze")
def analyze_runs(request: AnalyzeRequest, db: Session = Depends(get_db)):
    if request.run_ids:
        runs = db.query(models.AIRun).filter(models.AIRun.id.in_(request.run_ids)).all()
    else:
        runs = db.query(models.AIRun).all()
    analyzed = []
    for run in runs:
        analyze_run(db, run)
        analyzed.append(run.id)
    return {"analyzed": len(analyzed), "run_ids": analyzed}


@router.post("/analysis/run-full")
@router.post("/demo/run-full")  # backward-compatible alias
def run_full_analysis(db: Session = Depends(get_db)):
    """Load queries, run all, and analyze visibility."""
    csv_path = Path(__file__).resolve().parents[3] / "data" / "sample_queries.csv"
    from app.services.query_service import load_queries_from_csv

    if csv_path.exists():
        load_queries_from_csv(db, csv_path)

    runs = run_batch(db, RunBatchRequest(provider="mock"))
    return {
        "queries_loaded": db.query(models.Query).count(),
        "runs_completed": len(runs),
        "message": "Analysis complete",
    }


def _run_response(run: models.AIRun) -> AIRunResponse:
    return AIRunResponse(
        id=run.id,
        query_id=run.query_id,
        provider=run.provider,
        model=run.model,
        timestamp=run.timestamp,
        raw_answer=run.raw_answer,
        structured_answer=json.loads(run.structured_answer),
        latency_ms=run.latency_ms,
        status=run.status,
    )
