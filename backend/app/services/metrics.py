"""Metrics calculation for visibility analysis."""

from dataclasses import dataclass


@dataclass
class RunVisibility:
    mentioned: bool
    recommended: bool
    position: int | None
    has_boutiqaat_source: bool


VISIBILITY_WEIGHTS = {
    "mention": 0.20,
    "recommendation": 0.40,
    "top3": 0.25,
    "source_support": 0.15,
}


def compute_run_visibility_score(rv: RunVisibility) -> float:
    """Visibility Score for a single run (0-100)."""
    score = 0.0
    if rv.mentioned:
        score += VISIBILITY_WEIGHTS["mention"] * 100
    if rv.recommended:
        score += VISIBILITY_WEIGHTS["recommendation"] * 100
    if rv.recommended and rv.position is not None and rv.position <= 3:
        score += VISIBILITY_WEIGHTS["top3"] * 100
    if rv.has_boutiqaat_source:
        score += VISIBILITY_WEIGHTS["source_support"] * 100
    return round(score, 2)


def mention_rate(runs: list[RunVisibility]) -> float:
    if not runs:
        return 0.0
    return round(sum(1 for r in runs if r.mentioned) / len(runs) * 100, 2)


def recommendation_rate(runs: list[RunVisibility]) -> float:
    if not runs:
        return 0.0
    return round(sum(1 for r in runs if r.recommended) / len(runs) * 100, 2)


def average_position(runs: list[RunVisibility]) -> float | None:
    positions = [r.position for r in runs if r.recommended and r.position is not None]
    if not positions:
        return None
    return round(sum(positions) / len(positions), 2)


def top3_rate(runs: list[RunVisibility]) -> float:
    if not runs:
        return 0.0
    count = sum(1 for r in runs if r.recommended and r.position is not None and r.position <= 3)
    return round(count / len(runs) * 100, 2)


def aggregate_visibility_score(runs: list[RunVisibility]) -> float:
    if not runs:
        return 0.0
    return round(sum(compute_run_visibility_score(r) for r in runs) / len(runs), 2)


def source_coverage(runs: list[RunVisibility]) -> float:
    recommended = [r for r in runs if r.recommended]
    if not recommended:
        return 0.0
    supported = sum(1 for r in recommended if r.has_boutiqaat_source)
    return round(supported / len(recommended) * 100, 2)
