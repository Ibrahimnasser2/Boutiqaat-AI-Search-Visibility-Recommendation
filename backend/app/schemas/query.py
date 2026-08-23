from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


IntentType = Literal["discovery", "transactional", "comparison", "product_specific", "local"]
CategoryType = Literal["skincare", "makeup", "beauty", "korean_beauty", "general_beauty"]


class QueryCreate(BaseModel):
    text: str = Field(..., min_length=3, max_length=500)
    intent: IntentType = "discovery"
    category: CategoryType = "beauty"
    geography: str = "GCC"


class QueryResponse(BaseModel):
    id: int
    text: str
    intent: str
    category: str
    geography: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryBulkCreate(BaseModel):
    queries: list[QueryCreate]
