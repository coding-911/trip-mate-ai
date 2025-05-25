# app/api/v1/routers/recommendation.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.recommendation_service import RecommendationService
from app.api.v1.schemas.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter(prefix="/recommend", tags=["recommendation"])

@router.post("", response_model=RecommendationResponse)
def recommend(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    try:
        schedule = RecommendationService.recommend_with_cache(
            method=request.method or "auto",
            user_id=request.user_id,
            tags=request.tags,
            days=request.days,
            per_day_count=request.per_day_count,
            db=db
        )
        return {"schedule": schedule}
    except Exception as e:
        print(">>> Recommend API Error:", e) 
        raise HTTPException(status_code=500, detail=str(e))
