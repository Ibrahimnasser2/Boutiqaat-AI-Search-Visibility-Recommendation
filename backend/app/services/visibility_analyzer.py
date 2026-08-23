"""Core visibility analysis orchestration."""

import json

from sqlalchemy.orm import Session

from app.db import models
from app.services.competitor_analyzer import extract_competitors
from app.services.entity_detection import (
    contains_boutiqaat,
    extract_boutiqaat_position,
    is_boutiqaat_recommended,
)
from app.services.metrics import RunVisibility, compute_run_visibility_score
from app.services.opportunity_analyzer import generate_opportunities
from app.services.source_analyzer import extract_sources


def analyze_run(db: Session, run: models.AIRun) -> models.VisibilityAnalysis:
    """Run full visibility analysis pipeline on an AI run."""
    structured = json.loads(run.structured_answer)

    boutiqaat_data = structured.get("boutiqaat", {})
    mentioned = boutiqaat_data.get("mentioned", False) or contains_boutiqaat(run.raw_answer)
    structured_rec = boutiqaat_data.get("recommended")
    recommended = is_boutiqaat_recommended(run.raw_answer, structured_rec)
    if structured_rec is True:
        recommended = True
    elif structured_rec is False and not recommended:
        recommended = False

    position = boutiqaat_data.get("position")
    if recommended and position is None:
        position = extract_boutiqaat_position(structured.get("recommendations", []))
    if not recommended:
        position = None

    competitors_data = extract_competitors(structured)
    sources_data = extract_sources(structured)
    has_boutiqaat_source = any(s["supports_boutiqaat"] for s in sources_data)

    rv = RunVisibility(
        mentioned=mentioned,
        recommended=recommended,
        position=position,
        has_boutiqaat_source=has_boutiqaat_source,
    )
    vis_score = compute_run_visibility_score(rv)
    confidence = 0.95 if structured.get("recommendations") else 0.7

    parts = []
    if mentioned:
        parts.append("Boutiqaat mentioned")
    else:
        parts.append("Boutiqaat not mentioned")
    if recommended:
        parts.append(f"recommended at position {position}")
    elif mentioned:
        parts.append("mentioned but not recommended")
    explanation = "; ".join(parts) + "."

    if run.visibility:
        vis = run.visibility
        vis.boutiqaat_mentioned = mentioned
        vis.boutiqaat_recommended = recommended
        vis.boutiqaat_position = position
        vis.competitor_count = len(competitors_data)
        vis.visibility_score = vis_score
        vis.confidence = confidence
        vis.explanation = explanation
    else:
        vis = models.VisibilityAnalysis(
            run_id=run.id,
            boutiqaat_mentioned=mentioned,
            boutiqaat_recommended=recommended,
            boutiqaat_position=position,
            competitor_count=len(competitors_data),
            visibility_score=vis_score,
            confidence=confidence,
            explanation=explanation,
        )
        db.add(vis)

    db.query(models.Competitor).filter(models.Competitor.run_id == run.id).delete()
    for c in competitors_data:
        db.add(
            models.Competitor(
                run_id=run.id,
                name=c["name"],
                position=c["position"],
                recommended=c["recommended"],
                evidence=c["evidence"],
            )
        )

    db.query(models.Source).filter(models.Source.run_id == run.id).delete()
    for s in sources_data:
        db.add(
            models.Source(
                run_id=run.id,
                url=s["url"],
                domain=s["domain"],
                title=s["title"],
                source_type=s["source_type"],
                supports_boutiqaat=s["supports_boutiqaat"],
                relevance_score=s["relevance_score"],
            )
        )

    visibility_dict = {
        "boutiqaat_mentioned": mentioned,
        "boutiqaat_recommended": recommended,
        "boutiqaat_position": position,
    }
    db.query(models.Opportunity).filter(models.Opportunity.run_id == run.id).delete()
    query_text = run.query.text if run.query else ""
    for opp in generate_opportunities(query_text, structured, visibility_dict, competitors_data, sources_data):
        db.add(
            models.Opportunity(
                run_id=run.id,
                category=opp["category"],
                severity=opp["severity"],
                title=opp["title"],
                explanation=opp["explanation"],
                recommendation=opp["recommendation"],
                evidence=opp["evidence"],
            )
        )

    db.commit()
    db.refresh(vis)
    return vis
