from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.schemas.itinerary_step import ItineraryStepCreateRequest, ItineraryStepUpdateRequest, ItineraryStepResponse
from app.services.itinerary_step_service import ItineraryStepService

router = APIRouter(prefix="/itinerary-step", tags=["itinerary_step"])

@router.post("", response_model=ItineraryStepResponse)
def create_itinerary_step(
    req: ItineraryStepCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        step = ItineraryStepService.create_step(
            user_id=req.user_id,
            location_id=req.location_id,
            date_=req.date,
            start_time=req.start_time,
            end_time=req.end_time,
            db=db,
            itinerary_id=req.itinerary_id
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
        print(">>> ItineraryStep Create API Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{itinerary_step_id}", response_model=ItineraryStepResponse)
def update_itinerary_step(
    itinerary_step_id: str,
    req: ItineraryStepUpdateRequest,
    db: Session = Depends(get_db)
):
    try:
        step = ItineraryStepService.update_step(itinerary_step_id, req.model_dump(exclude_unset=True), db)
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
        print(">>> ItineraryStep Update API Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{itinerary_step_id}")
def delete_itinerary_step(
    itinerary_step_id: str,
    db: Session = Depends(get_db)
):
    try:
        ItineraryStepService.delete_step(itinerary_step_id, db)
        return {"result": "success"}
    except Exception as e:
        print(">>> ItineraryStep Delete API Error:", e)
        raise HTTPException(status_code=500, detail=str(e)) 