from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import routes_analysis, routes_queries, routes_reports
from app.core.config import settings
from app.db.database import init_db

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="AI Search Visibility & Recommendation Analyzer",
    description="Measures observable AI-search visibility for Boutiqaat under controlled queries.",
    version="1.0.0",
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_queries.router)
app.include_router(routes_analysis.router)
app.include_router(routes_reports.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mock_mode": settings.mock_mode,
    }


@app.get("/")
def dashboard():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "API running. Install frontend or use /docs"}
