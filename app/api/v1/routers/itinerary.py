from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.schemas.itinerary import ItineraryStepCreateRequest, ItineraryStepResponse
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/itinerary", tags=["itinerary"])

@router.post("/step", response_model=ItineraryStepResponse)
def add_itinerary_step(
    req: ItineraryStepCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        step = ItineraryService.add_step(
            user_id=req.user_id,
            location_id=req.location_id,
            date_=req.date,
            start_time=req.start_time,
            end_time=req.end_time,
            db=db
        )
        return ItineraryStepResponse(
            itinerary_id=step.itinerary_id,
            step_id=step.id,
            step_order=step.step_order,
            location_id=step.location_id,
            date=step.date,
            start_time=step.start_time,
            end_time=step.end_time
        )
    except Exception as e:
        print(">>> Itinerary API Error:", e)
        raise HTTPException(status_code=500, detail=str(e)) 