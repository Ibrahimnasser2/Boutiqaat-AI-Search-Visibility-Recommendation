from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    company: str
    position: int | None = None
    recommended: bool = True
    reason: str = ""


class BoutiqaatInfo(BaseModel):
    mentioned: bool = False
    recommended: bool = False
    position: int | None = None
    reason: str = ""


class SourceItem(BaseModel):
    url: str = ""
    domain: str = ""
    title: str = ""


class StructuredAnswer(BaseModel):
    answer_summary: str = ""
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    boutiqaat: BoutiqaatInfo = Field(default_factory=BoutiqaatInfo)
    sources: list[SourceItem] = Field(default_factory=list)


class AIRunCreate(BaseModel):
    query_id: int
    provider: str = "mock"


class AIRunResponse(BaseModel):
    id: int
    query_id: int
    provider: str
    model: str
    timestamp: datetime
    raw_answer: str
    structured_answer: dict[str, Any]
    latency_ms: float
    status: str

    model_config = {"from_attributes": True}


class RunBatchRequest(BaseModel):
    query_ids: list[int] | None = None
    provider: str = "mock"
