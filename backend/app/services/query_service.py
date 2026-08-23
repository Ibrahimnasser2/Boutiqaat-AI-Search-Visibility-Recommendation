import csv
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db import models
from app.schemas.answer import RunBatchRequest
from app.schemas.query import QueryCreate
from app.services.llm_service import get_llm_provider
from app.services.visibility_analyzer import analyze_run


def create_query(db: Session, data: QueryCreate) -> models.Query:
    existing = db.query(models.Query).filter(models.Query.text == data.text).first()
    if existing:
        return existing
    q = models.Query(
        text=data.text,
        intent=data.intent,
        category=data.category,
        geography=data.geography,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def list_queries(db: Session) -> list[models.Query]:
    return db.query(models.Query).order_by(models.Query.id).all()


def load_queries_from_csv(db: Session, csv_path: Path) -> int:
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            create_query(
                db,
                QueryCreate(
                    text=row["text"],
                    intent=row.get("intent", "discovery"),
                    category=row.get("category", "beauty"),
                    geography=row.get("geography", "GCC"),
                ),
            )
            count += 1
    return count


def run_single_query(db: Session, query_id: int, provider: str = "mock") -> models.AIRun:
    query = db.query(models.Query).filter(models.Query.id == query_id).first()
    if not query:
        raise ValueError(f"Query {query_id} not found")

    llm = get_llm_provider(provider)
    response = llm.run_query(query.text)

    run = models.AIRun(
        query_id=query.id,
        provider=response.provider,
        model=response.model,
        raw_answer=response.raw_answer,
        structured_answer=response.structured.model_dump_json(),
        latency_ms=response.latency_ms,
        status="completed",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    analyze_run(db, run)
    return run


def run_batch(db: Session, request: RunBatchRequest) -> list[models.AIRun]:
    if request.query_ids:
        queries = db.query(models.Query).filter(models.Query.id.in_(request.query_ids)).all()
    else:
        queries = db.query(models.Query).all()

    runs = []
    for q in queries:
        try:
            runs.append(run_single_query(db, q.id, request.provider))
        except Exception as e:
            logger.error("Failed run for query %s: %s", q.id, e)
    return runs


def get_run(db: Session, run_id: int) -> models.AIRun | None:
    return db.query(models.AIRun).filter(models.AIRun.id == run_id).first()


def list_runs(db: Session) -> list[models.AIRun]:
    return db.query(models.AIRun).order_by(models.AIRun.id.desc()).all()
