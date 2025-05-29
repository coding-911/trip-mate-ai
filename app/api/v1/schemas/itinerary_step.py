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
