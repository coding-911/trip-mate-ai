# app/api/v1/schemas/itinerary.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date

class ItineraryBase(BaseModel):
    user_id: UUID
    start_date: date
    end_date: date
    use_yn: Optional[str] = "Y"
    delete_yn: Optional[str] = "N"

class ItineraryCreate(ItineraryBase):
    pass

class Itinerary(ItineraryBase):
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

class ItineraryStepResponse(BaseModel):
    itinerary_id: UUID
    step_id: UUID
    step_order: int
    location_id: UUID
    date: date
    start_time: datetime
    end_time: datetime
