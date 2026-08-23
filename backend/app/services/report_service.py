"""Aggregate analysis metrics and report generation."""

import csv
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session, joinedload

from app.db import models
from app.schemas.analysis import (
    AnalysisDetail,
    CompetitorAggregate,
    IntentBreakdown,
    OverviewMetrics,
)
from app.services.competitor_analyzer import aggregate_competitors
from app.services.metrics import (
    RunVisibility,
    aggregate_visibility_score,
    average_position,
    mention_rate,
    recommendation_rate,
    source_coverage,
    top3_rate,
)
from app.services.source_analyzer import source_analysis_summary


def _run_visibilities(db: Session) -> list[tuple[models.AIRun, RunVisibility]]:
    runs = (
        db.query(models.AIRun)
        .options(joinedload(models.AIRun.visibility), joinedload(models.AIRun.sources))
        .filter(models.AIRun.status == "completed")
        .all()
    )
    result = []
    for run in runs:
        if not run.visibility:
            continue
        v = run.visibility
        has_src = any(s.supports_boutiqaat for s in run.sources)
        result.append(
            (
                run,
                RunVisibility(
                    mentioned=v.boutiqaat_mentioned,
                    recommended=v.boutiqaat_recommended,
                    position=v.boutiqaat_position,
                    has_boutiqaat_source=has_src,
                ),
            )
        )
    return result


def get_overview(db: Session) -> OverviewMetrics:
    total_queries = db.query(models.Query).count()
    total_runs = db.query(models.AIRun).count()
    pairs = _run_visibilities(db)
    rvs = [rv for _, rv in pairs]

    return OverviewMetrics(
        total_queries=total_queries,
        total_runs=total_runs,
        mention_rate=mention_rate(rvs),
        recommendation_rate=recommendation_rate(rvs),
        average_position=average_position(rvs),
        top3_rate=top3_rate(rvs),
        visibility_score=aggregate_visibility_score(rvs),
        source_coverage=source_coverage(rvs),
    )


def get_intent_breakdown(db: Session) -> list[IntentBreakdown]:
    pairs = _run_visibilities(db)
    by_intent: dict[str, list[RunVisibility]] = {}
    counts: dict[str, int] = {}

    for run, rv in pairs:
        intent = run.query.intent if run.query else "unknown"
        by_intent.setdefault(intent, []).append(rv)
        counts[intent] = counts.get(intent, 0) + 1

    return [
        IntentBreakdown(
            intent=intent,
            query_count=counts.get(intent, 0),
            mention_rate=mention_rate(rvs),
            recommendation_rate=recommendation_rate(rvs),
            visibility_score=aggregate_visibility_score(rvs),
        )
        for intent, rvs in sorted(by_intent.items())
    ]


def get_competitor_aggregates(db: Session) -> list[CompetitorAggregate]:
    total_runs = db.query(models.AIRun).count() or 1
    competitors = db.query(models.Competitor).all()
    records = [
        {
            "name": c.name,
            "position": c.position,
            "recommended": c.recommended,
        }
        for c in competitors
    ]
    agg = aggregate_competitors(records, total_runs)
    return [CompetitorAggregate(**a) for a in agg]


def get_opportunities(db: Session, severity: str | None = None) -> list[models.Opportunity]:
    q = db.query(models.Opportunity).order_by(models.Opportunity.id.desc())
    if severity:
        q = q.filter(models.Opportunity.severity == severity)
    return q.all()


def get_analysis_detail(db: Session, run_id: int) -> AnalysisDetail | None:
    run = (
        db.query(models.AIRun)
        .options(
            joinedload(models.AIRun.query),
            joinedload(models.AIRun.visibility),
            joinedload(models.AIRun.competitors),
            joinedload(models.AIRun.sources),
            joinedload(models.AIRun.opportunities),
        )
        .filter(models.AIRun.id == run_id)
        .first()
    )
    if not run or not run.visibility:
        return None

    return AnalysisDetail(
        run_id=run.id,
        query_id=run.query_id,
        query_text=run.query.text if run.query else "",
        provider=run.provider,
        model=run.model,
        raw_answer=run.raw_answer,
        structured_answer=json.loads(run.structured_answer),
        visibility=run.visibility,
        competitors=run.competitors,
        sources=run.sources,
        opportunities=run.opportunities,
    )


def generate_report(db: Session, output_dir: Path) -> dict:
    overview = get_overview(db)
    intents = get_intent_breakdown(db)
    competitors = get_competitor_aggregates(db)
    opportunities = get_opportunities(db)

    pairs = _run_visibilities(db)
    sources_by_run = []
    recommended_count = 0
    for run, rv in pairs:
        sources_by_run.append(
            [
                {
                    "supports_boutiqaat": s.supports_boutiqaat,
                    "source_type": s.source_type,
                    "domain": s.domain,
                }
                for s in run.sources
            ]
        )
        if rv.recommended:
            recommended_count += 1

    source_summary = source_analysis_summary(sources_by_run, recommended_count or 1)

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "title": "Boutiqaat AI Search Visibility Report",
        "methodology": (
            "This report measures observable AI-search visibility under controlled queries. "
            "It does NOT reverse-engineer proprietary ranking algorithms. "
            "Observations (mention rates, rankings) are distinguished from inferences (opportunity explanations)."
        ),
        "executive_summary": {
            "total_queries_analyzed": overview.total_runs,
            "mention_rate_pct": overview.mention_rate,
            "recommendation_rate_pct": overview.recommendation_rate,
            "visibility_score_summary": overview.visibility_score,
            "average_position": overview.average_position,
            "top3_rate_pct": overview.top3_rate,
        },
        "overall_visibility": overview.model_dump(),
        "visibility_by_intent": [i.model_dump() for i in intents],
        "competitor_comparison": [c.model_dump() for c in competitors],
        "source_analysis": source_summary,
        "top_opportunities": [
            {
                "severity": o.severity,
                "title": o.title,
                "category": o.category,
                "explanation": o.explanation,
                "recommendation": o.recommendation,
                "evidence": o.evidence,
            }
            for o in opportunities[:15]
        ],
        "limitations": [
            "LLM responses are non-deterministic (except mock mode).",
            "Limited query set — not exhaustive of all customer questions.",
            "Single provider in initial release; ChatGPT/Perplexity/Google may differ.",
            "No access to proprietary ranking algorithms.",
            "Source availability varies by provider.",
            "Correlation does not imply causation for opportunity signals.",
        ],
        "next_steps": [
            "Expand query set across intents and geographies.",
            "Add multi-provider comparison (OpenAI, Perplexity API).",
            "Schedule recurring monitoring runs.",
            "Track visibility trends over time.",
            "Prioritize high-severity opportunities for content/PR actions.",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "sample_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    csv_path = output_dir / "sample_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["mention_rate", overview.mention_rate])
        writer.writerow(["recommendation_rate", overview.recommendation_rate])
        writer.writerow(["visibility_score", overview.visibility_score])
        writer.writerow(["average_position", overview.average_position or "N/A"])
        writer.writerow(["top3_rate", overview.top3_rate])
        writer.writerow(["source_coverage", overview.source_coverage])
        for c in competitors:
            writer.writerow([f"competitor_{c.name}_rec_rate", c.recommendation_rate])

    html_path = output_dir / "sample_report.html"
    html_path.write_text(_render_html(report), encoding="utf-8")

    return {"json": str(json_path), "csv": str(csv_path), "html": str(html_path), "report": report}


def _render_html(report: dict) -> str:
    es = report["executive_summary"]
    opps = report["top_opportunities"][:8]
    comps = report["competitor_comparison"][:8]

    opp_rows = "".join(
        f"<tr><td>{o['severity']}</td><td>{o['title']}</td><td>{o['recommendation']}</td></tr>"
        for o in opps
    )
    comp_rows = "".join(
        f"<tr><td>{c['name']}</td><td>{c['mention_rate']}%</td><td>{c['recommendation_rate']}%</td>"
        f"<td>{c['average_position'] or 'N/A'}</td><td>{c['top3_rate']}%</td></tr>"
        for c in comps
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{report['title']}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #1a1a2e; }}
    h1 {{ color: #6c3fc5; }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
    .card {{ background: #f8f7ff; border-radius: 8px; padding: 1rem; }}
    .card strong {{ font-size: 1.5rem; color: #6c3fc5; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #6c3fc5; color: white; }}
    .note {{ background: #fff8e1; padding: 1rem; border-radius: 8px; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>{report['title']}</h1>
  <p><em>Generated: {report['generated_at']}</em></p>
  <div class="note">{report['methodology']}</div>
  <h2>Executive Summary</h2>
  <div class="metrics">
    <div class="card"><div>Mention Rate</div><strong>{es['mention_rate_pct']}%</strong></div>
    <div class="card"><div>Recommendation Rate</div><strong>{es['recommendation_rate_pct']}%</strong></div>
    <div class="card"><div>Visibility Score</div><strong>{es['visibility_score_summary']}</strong></div>
    <div class="card"><div>Avg Position</div><strong>{es['average_position'] or 'N/A'}</strong></div>
    <div class="card"><div>Top-3 Rate</div><strong>{es['top3_rate_pct']}%</strong></div>
    <div class="card"><div>Queries Analyzed</div><strong>{es['total_queries_analyzed']}</strong></div>
  </div>
  <h2>Competitor Comparison</h2>
  <table>
    <tr><th>Company</th><th>Mention Rate</th><th>Rec Rate</th><th>Avg Pos</th><th>Top-3 Rate</th></tr>
    {comp_rows}
  </table>
  <h2>Top Opportunities</h2>
  <table>
    <tr><th>Severity</th><th>Title</th><th>Recommendation</th></tr>
    {opp_rows}
  </table>
  <h2>Limitations</h2>
  <ul>{''.join(f'<li>{l}</li>' for l in report['limitations'])}</ul>
  <h2>Next Steps</h2>
  <ul>{''.join(f'<li>{n}</li>' for n in report['next_steps'])}</ul>
</body>
</html>"""
