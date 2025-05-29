from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.itinerary import Itinerary
from app.db.models.itinerary_step import ItineraryStep
from app.api.v1.schemas.itinerary import ItineraryWithStepsResponse, ItineraryResponse
from app.api.v1.schemas.itinerary_step import ItineraryStepResponse
from fastapi import HTTPException

def get_user_itineraries(user_id: str, db: Session) -> List[ItineraryWithStepsResponse]:
    user_uuid = UUID(user_id)
    itineraries = db.query(Itinerary).filter(
        Itinerary.user_id == user_uuid,
        Itinerary.delete_yn == 'N',
        Itinerary.use_yn == 'Y',
    ).order_by(Itinerary.start_date).all()
    result = []
    for it in itineraries:
        steps = db.query(ItineraryStep).filter(
            ItineraryStep.itinerary_id == it.id,
            ItineraryStep.delete_yn == 'N',
            ItineraryStep.use_yn == 'Y',
        ).order_by(ItineraryStep.date, ItineraryStep.start_time).all()
        result.append(ItineraryWithStepsResponse(
            itinerary=ItineraryResponse(
                id=it.id,
                start_date=it.start_date,
                end_date=it.end_date,
                use_yn=it.use_yn,
                delete_yn=it.delete_yn,
                created_at=it.created_at,
                updated_at=it.updated_at,
                deleted_at=it.deleted_at,
            ),
            steps=[
                ItineraryStepResponse(
                    itinerary_id=step.itinerary_id,
                    step_id=step.id,
                    step_order=step.step_order,
                    location_id=step.location_id,
                    date=step.date,
                    start_time=step.start_time,
                    end_time=step.end_time,
                ) for step in steps
            ]
        ))
    return result

def delete_itinerary_with_steps(itinerary_id: str, db: Session) -> None:
    itinerary = db.query(Itinerary).filter(Itinerary.id == UUID(itinerary_id), Itinerary.delete_yn == 'N').first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="해당 일정이 존재하지 않거나 이미 삭제됨")
    itinerary.delete_yn = 'Y'
    db.add(itinerary)
    steps = db.query(ItineraryStep).filter(ItineraryStep.itinerary_id == itinerary.id, ItineraryStep.delete_yn == 'N').all()
    for step in steps:
        step.delete_yn = 'Y'
        db.add(step)
    db.commit() 