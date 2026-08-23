from pydantic import BaseModel, Field


class VisibilityResponse(BaseModel):
    id: int
    run_id: int
    boutiqaat_mentioned: bool
    boutiqaat_recommended: bool
    boutiqaat_position: int | None
    competitor_count: int
    visibility_score: float
    confidence: float
    explanation: str

    model_config = {"from_attributes": True}


class CompetitorResponse(BaseModel):
    id: int
    run_id: int
    name: str
    position: int | None
    recommended: bool
    evidence: str

    model_config = {"from_attributes": True}


class SourceResponse(BaseModel):
    id: int
    run_id: int
    url: str
    domain: str
    title: str
    source_type: str
    supports_boutiqaat: bool
    relevance_score: float

    model_config = {"from_attributes": True}


class OpportunityResponse(BaseModel):
    id: int
    run_id: int
    category: str
    severity: str
    title: str
    explanation: str
    recommendation: str
    evidence: str

    model_config = {"from_attributes": True}


class OverviewMetrics(BaseModel):
    total_queries: int
    total_runs: int
    mention_rate: float
    recommendation_rate: float
    average_position: float | None
    top3_rate: float
    visibility_score: float
    source_coverage: float


class IntentBreakdown(BaseModel):
    intent: str
    query_count: int
    mention_rate: float
    recommendation_rate: float
    visibility_score: float


class CompetitorAggregate(BaseModel):
    name: str
    mention_count: int
    recommendation_count: int
    mention_rate: float
    recommendation_rate: float
    average_position: float | None
    top3_rate: float


class AnalysisDetail(BaseModel):
    run_id: int
    query_id: int
    query_text: str
    provider: str
    model: str
    raw_answer: str
    structured_answer: dict
    visibility: VisibilityResponse
    competitors: list[CompetitorResponse]
    sources: list[SourceResponse]
    opportunities: list[OpportunityResponse]


class AnalyzeRequest(BaseModel):
    run_ids: list[int] | None = None
