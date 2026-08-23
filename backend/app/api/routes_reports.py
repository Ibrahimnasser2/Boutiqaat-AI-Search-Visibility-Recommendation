from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analysis import (
    AnalysisDetail,
    CompetitorAggregate,
    IntentBreakdown,
    OpportunityResponse,
    OverviewMetrics,
)
from app.services.report_service import (
    generate_report,
    get_analysis_detail,
    get_competitor_aggregates,
    get_intent_breakdown,
    get_opportunities,
    get_overview,
)

router = APIRouter(prefix="/api", tags=["analysis", "reports"])


@router.get("/analysis/overview", response_model=OverviewMetrics)
def analysis_overview(db: Session = Depends(get_db)):
    return get_overview(db)


@router.get("/analysis/intents", response_model=list[IntentBreakdown])
def analysis_intents(db: Session = Depends(get_db)):
    return get_intent_breakdown(db)


@router.get("/analysis/competitors", response_model=list[CompetitorAggregate])
def analysis_competitors(db: Session = Depends(get_db)):
    return get_competitor_aggregates(db)


@router.get("/analysis/opportunities", response_model=list[OpportunityResponse])
def analysis_opportunities(severity: str | None = None, db: Session = Depends(get_db)):
    return get_opportunities(db, severity)


@router.get("/analysis/runs/{run_id}", response_model=AnalysisDetail)
def analysis_run_detail(run_id: int, db: Session = Depends(get_db)):
    detail = get_analysis_detail(db, run_id)
    if not detail:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Analysis not found")
    return detail


@router.get("/reports/sample")
def sample_report(db: Session = Depends(get_db)):
    output_dir = Path(__file__).resolve().parents[3] / "reports"
    result = generate_report(db, output_dir)
    return {
        "message": "Report generated",
        "files": {"json": result["json"], "csv": result["csv"], "html": result["html"]},
        "summary": result["report"]["executive_summary"],
    }


@router.get("/reports/sample/html")
def sample_report_html(db: Session = Depends(get_db)):
    output_dir = Path(__file__).resolve().parents[3] / "reports"
    result = generate_report(db, output_dir)
    return FileResponse(result["html"], media_type="text/html")
