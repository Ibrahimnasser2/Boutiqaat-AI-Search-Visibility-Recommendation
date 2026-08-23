from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.query import QueryBulkCreate, QueryCreate, QueryResponse
from app.services.query_service import create_query, list_queries, load_queries_from_csv

router = APIRouter(prefix="/api/queries", tags=["queries"])


@router.post("", response_model=QueryResponse)
def add_query(data: QueryCreate, db: Session = Depends(get_db)):
    return create_query(db, data)


@router.post("/bulk", response_model=list[QueryResponse])
def add_queries_bulk(data: QueryBulkCreate, db: Session = Depends(get_db)):
    return [create_query(db, q) for q in data.queries]


@router.get("", response_model=list[QueryResponse])
def get_queries(db: Session = Depends(get_db)):
    return list_queries(db)


@router.post("/load-sample")
def load_sample_queries(db: Session = Depends(get_db)):
    from pathlib import Path

    csv_path = Path(__file__).resolve().parents[3] / "data" / "sample_queries.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Sample queries CSV not found")
    count = load_queries_from_csv(db, csv_path)
    return {"loaded": count, "message": f"Loaded {count} queries"}
