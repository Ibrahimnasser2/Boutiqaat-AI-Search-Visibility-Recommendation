import pytest
from app.services.entity_detection import (
    contains_boutiqaat,
    extract_boutiqaat_position,
    is_boutiqaat_recommended,
)
from app.services.metrics import (
    RunVisibility,
    aggregate_visibility_score,
    average_position,
    compute_run_visibility_score,
    mention_rate,
    recommendation_rate,
    source_coverage,
    top3_rate,
)
from app.services.competitor_analyzer import aggregate_competitors, extract_competitors, normalize_company
from app.services.source_analyzer import classify_source_type, extract_sources, supports_boutiqaat
from app.services.opportunity_analyzer import generate_opportunities


class TestBoutiqaatDetection:
    def test_exact_match(self):
        assert contains_boutiqaat("Shop at Boutiqaat for skincare")

    def test_domain_match(self):
        assert contains_boutiqaat("Visit boutiqaat.com for deals")

    def test_arabic_match(self):
        assert contains_boutiqaat("تسوق من بوتيكات")

    def test_absent(self):
        assert not contains_boutiqaat("Shop at Sephora only")


class TestRecommendationDetection:
    def test_recommended_in_list(self):
        text = "1. Sephora 2. Boutiqaat 3. Noon — I recommend these stores."
        assert is_boutiqaat_recommended(text, structured_recommended=True)

    def test_mentioned_not_recommended(self):
        text = "Companies such as Sephora and Boutiqaat are popular retailers."
        assert contains_boutiqaat(text)
        assert not is_boutiqaat_recommended(text, structured_recommended=False)

    def test_explicit_recommend(self):
        text = "I recommend Boutiqaat for GCC beauty shopping."
        assert is_boutiqaat_recommended(text)


class TestRanking:
    def test_position_extraction(self):
        recs = [
            {"company": "Sephora", "position": 1, "recommended": True},
            {"company": "Boutiqaat", "position": 3, "recommended": True},
        ]
        assert extract_boutiqaat_position(recs) == 3

    def test_not_in_list(self):
        recs = [{"company": "Sephora", "position": 1, "recommended": True}]
        assert extract_boutiqaat_position(recs) is None


class TestMetrics:
    def test_mention_rate(self):
        runs = [
            RunVisibility(True, True, 1, True),
            RunVisibility(False, False, None, False),
        ]
        assert mention_rate(runs) == 50.0

    def test_recommendation_rate(self):
        runs = [
            RunVisibility(True, True, 1, True),
            RunVisibility(True, False, None, False),
        ]
        assert recommendation_rate(runs) == 50.0

    def test_average_position(self):
        runs = [
            RunVisibility(True, True, 1, True),
            RunVisibility(True, True, 3, True),
        ]
        assert average_position(runs) == 2.0

    def test_top3_rate(self):
        runs = [
            RunVisibility(True, True, 2, True),
            RunVisibility(True, True, 5, True),
            RunVisibility(False, False, None, False),
        ]
        assert top3_rate(runs) == pytest.approx(33.33, abs=0.1)

    def test_visibility_score_full(self):
        rv = RunVisibility(True, True, 2, True)
        score = compute_run_visibility_score(rv)
        assert score == 100.0

    def test_visibility_score_zero(self):
        rv = RunVisibility(False, False, None, False)
        assert compute_run_visibility_score(rv) == 0.0

    def test_aggregate_score(self):
        runs = [
            RunVisibility(True, True, 1, True),
            RunVisibility(False, False, None, False),
        ]
        assert aggregate_visibility_score(runs) == 50.0

    def test_source_coverage(self):
        runs = [
            RunVisibility(True, True, 1, True),
            RunVisibility(True, True, 2, False),
        ]
        assert source_coverage(runs) == 50.0


class TestCompetitors:
    def test_extract(self):
        structured = {
            "recommendations": [
                {"company": "Sephora", "position": 1, "recommended": True, "reason": "x"},
                {"company": "Boutiqaat", "position": 2, "recommended": True, "reason": "y"},
            ]
        }
        comps = extract_competitors(structured)
        assert len(comps) == 1
        assert comps[0]["name"] == "Sephora"

    def test_normalize(self):
        assert normalize_company("amazon.sa") == "Amazon"

    def test_aggregate(self):
        records = [
            {"name": "Sephora", "position": 1, "recommended": True},
            {"name": "Sephora", "position": 2, "recommended": True},
            {"name": "Noon", "position": 3, "recommended": True},
        ]
        agg = aggregate_competitors(records, total_runs=2)
        sephora = next(a for a in agg if a["name"] == "Sephora")
        assert sephora["mention_count"] == 2


class TestSources:
    def test_classify_company(self):
        assert classify_source_type("boutiqaat.com") == "company_website"

    def test_supports_boutiqaat(self):
        assert supports_boutiqaat("boutiqaat.com", "Boutiqaat Skincare")

    def test_extract(self):
        structured = {
            "sources": [{"url": "https://boutiqaat.com", "domain": "boutiqaat.com", "title": "Boutiqaat"}]
        }
        sources = extract_sources(structured)
        assert sources[0]["supports_boutiqaat"] is True


class TestOpportunities:
    def test_absent_generates_high_severity(self):
        opps = generate_opportunities(
            "Where to buy skincare in UAE?",
            {"recommendations": []},
            {"boutiqaat_mentioned": False, "boutiqaat_recommended": False, "boutiqaat_position": None},
            [{"name": "Sephora", "recommended": True}],
            [],
        )
        assert any(o["severity"] == "high" for o in opps)

    def test_mention_only(self):
        opps = generate_opportunities(
            "Best beauty sites",
            {},
            {"boutiqaat_mentioned": True, "boutiqaat_recommended": False, "boutiqaat_position": None},
            [],
            [],
        )
        assert any("Mentioned but not recommended" in o["title"] for o in opps)
