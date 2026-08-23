"""Classify and analyze sources from AI responses."""

import re
from urllib.parse import urlparse

BOUTIQAAT_DOMAINS = {"boutiqaat.com", "www.boutiqaat.com"}

SOURCE_TYPE_RULES = [
    (r"boutiqaat\.com|sephora\.|noon\.|amazon\.|namshi\.|yesstyle\.|iherb\.", "company_website"),
    (r"reddit\.|quora\.|trustpilot", "social/community"),
    (r"review|reviews", "review"),
    (r"news|reuters|arabianbusiness|forbes", "news"),
    (r"blog|medium", "blog"),
    (r"vogue|elle|harpers", "editorial"),
]


def _domain_from_url(url: str) -> str:
    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def classify_source_type(domain: str, title: str = "") -> str:
    combined = f"{domain} {title}".lower()
    for pattern, source_type in SOURCE_TYPE_RULES:
        if re.search(pattern, combined):
            return source_type
    return "unknown"


def supports_boutiqaat(domain: str, title: str = "", url: str = "") -> bool:
    d = domain.lower().replace("www.", "")
    if d in BOUTIQAAT_DOMAINS or "boutiqaat" in d:
        return True
    combined = f"{title} {url}".lower()
    return "boutiqaat" in combined or "بوتيكات" in combined


def extract_sources(structured: dict) -> list[dict]:
    sources = []
    for item in structured.get("sources", []):
        url = item.get("url", "")
        domain = item.get("domain") or _domain_from_url(url)
        title = item.get("title", "")
        stype = classify_source_type(domain, title)
        sources.append(
            {
                "url": url,
                "domain": domain,
                "title": title,
                "source_type": stype,
                "supports_boutiqaat": supports_boutiqaat(domain, title, url),
                "relevance_score": 0.9 if stype in ("company_website", "editorial") else 0.6,
            }
        )
    return sources


def source_analysis_summary(sources_by_run: list[list[dict]], recommended_runs: int) -> dict:
    boutiqaat_supported = sum(
        1 for sources in sources_by_run if any(s["supports_boutiqaat"] for s in sources)
    )
    first_party = sum(1 for sources in sources_by_run if any(s["source_type"] == "company_website" and s["supports_boutiqaat"] for s in sources))
    third_party = sum(
        1
        for sources in sources_by_run
        if any(s["supports_boutiqaat"] and s["source_type"] != "company_website" for s in sources)
    )
    competitor_domains: dict[str, int] = {}
    for sources in sources_by_run:
        for s in sources:
            if not s["supports_boutiqaat"] and s["source_type"] == "company_website":
                competitor_domains[s["domain"]] = competitor_domains.get(s["domain"], 0) + 1

    return {
        "source_coverage": round(boutiqaat_supported / recommended_runs * 100, 2) if recommended_runs else 0,
        "first_party_coverage": first_party,
        "third_party_coverage": third_party,
        "competitor_source_dominance": sorted(
            [{"domain": k, "count": v} for k, v in competitor_domains.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:5],
    }
