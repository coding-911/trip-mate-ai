from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.services.recommendation_service import RecommendationService
from app.db.session import get_db
from app.api.v1.schemas.location import LocationResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class RecommendMVPRequest(BaseModel):
    tags: List[str]
    days: int
    per_day_count: int = 5

    model_config = {"from_attributes": True}

@router.post("/mvp", response_model=List[List[LocationResponse]])
def recommend_mvp(req: RecommendMVPRequest, db: Session = Depends(get_db)):
    return RecommendationService.recommend_mvp(
        tags=req.tags,
        days=req.days,
        per_day_count=req.per_day_count,
        db=db
    )
