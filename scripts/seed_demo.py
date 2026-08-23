"""Load customer query data and run the full analysis pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.database import SessionLocal, init_db
from app.schemas.answer import RunBatchRequest
from app.services.query_service import load_queries_from_csv, run_batch
from app.services.report_service import generate_report


def main():
    init_db()
    db = SessionLocal()
    csv_path = Path(__file__).resolve().parents[1] / "data" / "sample_queries.csv"
    count = load_queries_from_csv(db, csv_path)
    print(f"Loaded {count} queries")
    runs = run_batch(db, RunBatchRequest(provider="mock"))
    print(f"Completed {len(runs)} AI runs with analysis")
    reports_dir = Path(__file__).resolve().parents[1] / "reports"
    result = generate_report(db, reports_dir)
    print(f"Report generated: {result['json']}")
    db.close()


if __name__ == "__main__":
    main()
