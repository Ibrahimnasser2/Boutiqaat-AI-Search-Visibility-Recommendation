"""Generate visibility improvement opportunities from analysis signals."""

from app.services.entity_detection import contains_boutiqaat


def generate_opportunities(
    query_text: str,
    structured: dict,
    visibility: dict,
    competitors: list[dict],
    sources: list[dict],
) -> list[dict]:
    """Generate potential (not proven) visibility opportunities."""
    opportunities = []
    mentioned = visibility["boutiqaat_mentioned"]
    recommended = visibility["boutiqaat_recommended"]
    position = visibility.get("boutiqaat_position")
    query_lower = query_text.lower()

    if not mentioned:
        opportunities.append(
            {
                "category": "weak_topical_authority",
                "severity": "high",
                "title": "Boutiqaat absent from AI recommendation set",
                "explanation": "Observed signal: Boutiqaat did not appear in this AI-generated answer for a relevant beauty retail query.",
                "recommendation": "Strengthen topical authority content around this query theme (GCC beauty/skincare retail).",
                "evidence": f"Query: '{query_text}' — zero mention in response.",
            }
        )
        if any(g in query_lower for g in ["saudi", "uae", "kuwait", "gcc", "middle east"]):
            opportunities.append(
                {
                    "category": "geographic_relevance_gap",
                    "severity": "high",
                    "title": "Potential geographic relevance gap",
                    "explanation": "Observed signal: Geo-specific query but Boutiqaat not surfaced.",
                    "recommendation": "Increase geo-targeted content and third-party GCC retail listicles mentioning Boutiqaat.",
                    "evidence": "Geographic intent detected without Boutiqaat presence.",
                }
            )

    elif mentioned and not recommended:
        opportunities.append(
            {
                "category": "poor_query_intent_alignment",
                "severity": "medium",
                "title": "Mentioned but not recommended",
                "explanation": "Observed signal: Boutiqaat appears in passing but is not in the active recommendation list.",
                "recommendation": "Align product/category landing pages with transactional query intent; pursue comparison content.",
                "evidence": "Mention-only context detected — not ranked as purchase destination.",
            }
        )

    if recommended and position and position > 3:
        opportunities.append(
            {
                "category": "competitor_dominance",
                "severity": "medium",
                "title": f"Boutiqaat ranked #{position} — outside top 3",
                "explanation": "Observed signal: Boutiqaat is recommended but outranked by competitors.",
                "recommendation": "Analyze top-ranked competitors' content and source footprint for this query type.",
                "evidence": f"Position {position} vs top competitors: {', '.join(c['name'] for c in competitors[:3])}",
            }
        )

    boutiqaat_sources = [s for s in sources if s.get("supports_boutiqaat")]
    third_party = [s for s in boutiqaat_sources if s.get("source_type") != "company_website"]
    if recommended and not third_party:
        opportunities.append(
            {
                "category": "insufficient_third_party_coverage",
                "severity": "high",
                "title": "No third-party sources supporting Boutiqaat",
                "explanation": "Observed signal: Recommendation lacks editorial/review sources citing Boutiqaat.",
                "recommendation": "Pursue authoritative third-party coverage (editorial, reviews, GCC retail guides).",
                "evidence": "Only first-party or no Boutiqaat sources in response.",
            }
        )

    if not boutiqaat_sources and (mentioned or recommended):
        opportunities.append(
            {
                "category": "insufficient_source_evidence",
                "severity": "medium",
                "title": "Missing source citations for Boutiqaat",
                "explanation": "Observed signal: Boutiqaat referenced without supporting URL citations.",
                "recommendation": "Ensure crawlable, citable pages exist for key product/category queries.",
                "evidence": "No Boutiqaat URLs in source list.",
            }
        )

    comp_count = len([c for c in competitors if c.get("recommended")])
    if comp_count >= 3 and (not recommended or (position and position > 2)):
        opportunities.append(
            {
                "category": "competitor_dominance",
                "severity": "high" if not recommended else "medium",
                "title": "Competitor-heavy recommendation landscape",
                "explanation": f"Observed signal: {comp_count} competitors actively recommended.",
                "recommendation": "Differentiate on GCC-specific assortment, Arabic content, and local brand partnerships.",
                "evidence": f"Competitors: {', '.join(c['name'] for c in competitors[:5])}",
            }
        )

    if any(k in query_lower for k in ["cosrx", "laneige", "korean", "sunscreen", "serum"]):
        if not recommended:
            opportunities.append(
                {
                    "category": "weak_product_information",
                    "severity": "medium",
                    "title": "Product-specific query — weak Boutiqaat visibility",
                    "explanation": "Observed signal: Product/brand-specific query did not surface Boutiqaat.",
                    "recommendation": "Enhance product detail pages and structured data for key K-beauty SKUs.",
                    "evidence": f"Product-specific query: '{query_text}'",
                }
            )

    if not opportunities:
        opportunities.append(
            {
                "category": "competitor_dominance",
                "severity": "low",
                "title": "Maintain visibility momentum",
                "explanation": "Observed signal: Boutiqaat performing well on this query.",
                "recommendation": "Monitor regularly and expand winning content patterns to similar queries.",
                "evidence": "Strong visibility on this query run.",
            }
        )

    return opportunities
