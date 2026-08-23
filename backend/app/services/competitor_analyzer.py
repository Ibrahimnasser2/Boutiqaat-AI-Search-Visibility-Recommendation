"""Analyze competitors from structured AI responses."""

from app.services.entity_detection import normalize_text

COMPANY_ALIASES = {
    "amazon.sa": "Amazon",
    "amazon.ae": "Amazon",
    "amazon": "Amazon",
    "sephora.ae": "Sephora",
    "sephora": "Sephora",
    "noon.com": "Noon",
    "noon": "Noon",
    "yesstyle": "YesStyle",
    "iherb": "iHerb",
    "namshi": "Namshi",
    "nice one": "Nice One",
    "niceonesa": "Nice One",
    "faces": "Faces",
    "boots": "Boots",
    "lookfantastic": "LookFantastic",
    "cult beauty": "Cult Beauty",
    "stylevana": "StyleVana",
}


def normalize_company(name: str) -> str:
    key = normalize_text(name)
    for alias, canonical in COMPANY_ALIASES.items():
        if alias in key:
            return canonical
    return name.strip().title()


def extract_competitors(structured: dict) -> list[dict]:
    competitors = []
    seen = set()
    for rec in structured.get("recommendations", []):
        name = normalize_company(rec.get("company", ""))
        if not name or name.lower() == "boutiqaat":
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        competitors.append(
            {
                "name": name,
                "position": rec.get("position"),
                "recommended": rec.get("recommended", True),
                "evidence": rec.get("reason", ""),
            }
        )
    return competitors


def aggregate_competitors(records: list[dict], total_runs: int) -> list[dict]:
    """Aggregate competitor stats across runs. records: list of competitor dicts with run context."""
    by_name: dict[str, dict] = {}
    for rec in records:
        name = rec["name"]
        if name not in by_name:
            by_name[name] = {
                "name": name,
                "mention_count": 0,
                "recommendation_count": 0,
                "positions": [],
                "top3_count": 0,
            }
        by_name[name]["mention_count"] += 1
        if rec.get("recommended"):
            by_name[name]["recommendation_count"] += 1
            pos = rec.get("position")
            if pos is not None:
                by_name[name]["positions"].append(pos)
                if pos <= 3:
                    by_name[name]["top3_count"] += 1

    result = []
    for stats in by_name.values():
        positions = stats["positions"]
        result.append(
            {
                "name": stats["name"],
                "mention_count": stats["mention_count"],
                "recommendation_count": stats["recommendation_count"],
                "mention_rate": round(stats["mention_count"] / total_runs * 100, 2) if total_runs else 0,
                "recommendation_rate": round(stats["recommendation_count"] / total_runs * 100, 2)
                if total_runs
                else 0,
                "average_position": round(sum(positions) / len(positions), 2) if positions else None,
                "top3_rate": round(stats["top3_count"] / total_runs * 100, 2) if total_runs else 0,
            }
        )
    return sorted(result, key=lambda x: x["recommendation_count"], reverse=True)
