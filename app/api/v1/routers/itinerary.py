from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from uuid import UUID
from typing import List
from app.api.v1.schemas.itinerary import ItineraryWithStepsResponse
from app.services.itinerary_service import get_user_itineraries, delete_itinerary_with_steps

router = APIRouter(prefix="/itinerary", tags=["itinerary"])

@router.get("/user/{user_id}", response_model=List[ItineraryWithStepsResponse])
def get_user_itineraries_router(user_id: str, db: Session = Depends(get_db)):
    try:
        return get_user_itineraries(user_id, db)
    except Exception as e:
        print(">>> Itinerary List API Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{itinerary_id}")
def delete_itinerary(itinerary_id: str, db: Session = Depends(get_db)):
    try:
        delete_itinerary_with_steps(itinerary_id, db)
        return {"result": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(">>> Itinerary Delete API Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

