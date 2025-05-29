# app/api/v1/schemas/itinerary_step.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date

class ItineraryStepBase(BaseModel):
    itinerary_id: UUID
    location_id: UUID
    step_order: int
    date: date
    start_time: datetime
    end_time: datetime
    comment: Optional[str]

class ItineraryStepCreate(ItineraryStepBase):
    pass

class ItineraryStep(ItineraryStepBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = { "from_attributes": True }

class ItineraryStepCreateRequest(BaseModel):
    user_id: str
    location_id: str
    date: date
    start_time: datetime
    end_time: datetime
    itinerary_id: Optional[str] = None

class ItineraryStepUpdateRequest(BaseModel):
    date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location_id: Optional[str] = None

class ItineraryStepResponse(BaseModel):
    itinerary_id: UUID
    step_id: UUID
    step_order: int
    location_id: UUID
    date: date
    start_time: datetime
    end_time: datetime
