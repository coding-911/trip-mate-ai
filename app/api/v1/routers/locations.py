# app/api/v1/routers/locations.py
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import List
from uuid import UUID

from app.services.kakao_service import KakaoService
from app.services.location_service import LocationService
from app.services.location_tag_service import LocationTagService

from app.api.v1.schemas.tag import TagNameRequest
from app.api.v1.schemas.location import LocationResponse
from app.api.v1.schemas.location_tag import LocationTagResponse


router = APIRouter(prefix="/location", tags=["location"])

@router.post("/search", response_model=List[LocationResponse])
def search_locations(keyword: str, size: int, db: Session = Depends(get_db)):
    try:
        results = KakaoService.search_and_save(keyword, db, size)
        return results
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/", response_model=List[LocationResponse])
def list_locations(db: Session = Depends(get_db)):
    return LocationService.get_active_locations(db)

@router.post("/{location_id}/tag", response_model=LocationTagResponse)
def add_tag_to_location(location_id: UUID, req: TagNameRequest, db: Session = Depends(get_db)):
    try:
        location_tag = LocationTagService.add_tag_to_location(location_id, req.tag_name, db)

        # 응답 스키마로 매핑
        return LocationTagResponse(
            location_id=location_tag.location_id,
            tag_id=location_tag.tag_id,
            tag_name=location_tag.tag.name  # 관계 통해 접근
        )

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")