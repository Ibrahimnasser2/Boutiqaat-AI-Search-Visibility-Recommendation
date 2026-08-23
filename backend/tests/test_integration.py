"""Integration test: query -> mock LLM -> analyzer -> metrics."""

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db import models
from app.schemas.query import QueryCreate
from app.services.query_service import create_query, run_single_query
from app.services.report_service import get_overview


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_full_pipeline(db):
    q = create_query(
        db,
        QueryCreate(
            text="What are the best online beauty stores in the Middle East?",
            intent="discovery",
            category="beauty",
        ),
    )
    run = run_single_query(db, q.id, provider="mock")
    assert run.status == "completed"
    assert run.visibility is not None or db.query(models.VisibilityAnalysis).filter_by(run_id=run.id).first()

    db.refresh(run)
    run = db.query(models.AIRun).filter_by(id=run.id).first()
    vis = db.query(models.VisibilityAnalysis).filter_by(run_id=run.id).first()
    assert vis is not None
    structured = json.loads(run.structured_answer)
    assert "recommendations" in structured

    overview = get_overview(db)
    assert overview.total_runs >= 1
