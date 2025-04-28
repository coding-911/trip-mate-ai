# app/api/v1/routers/locations.py
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.services.kakao_service import KakaoService
from app.db.session import get_db
from app.api.v1.schemas.location import LocationResponse

router = APIRouter(prefix="/location", tags=["location"])

@router.post("/search", response_model=List[LocationResponse])
def search_locations(keyword: str, size: int, db: Session = Depends(get_db)):
    try:
        results = KakaoService.search_and_save(keyword, db, size)
        return results
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: UUID, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == location_id, Location.delete_yn == 'N').first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc