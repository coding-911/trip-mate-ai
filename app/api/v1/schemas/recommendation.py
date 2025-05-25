from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from app.api.v1.schemas.location import LocationResponse  # 기존 Location 스키마 재사용

class RecommendationRequest(BaseModel):
    user_id: str
    tags: List[str]
    days: int
    per_day_count: int
    method: Optional[str] = "auto"  # "auto" | "model" | "mvp"

class RecommendationResponse(BaseModel):
    schedule: List[List[LocationResponse]]
