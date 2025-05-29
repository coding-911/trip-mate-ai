from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from app.api.v1.schemas.itinerary_step import ItineraryStepResponse

class ItineraryResponse(BaseModel):
    id: UUID
    start_date: date
    end_date: date
    use_yn: str
    delete_yn: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = {"from_attributes": True}

class ItineraryWithStepsResponse(BaseModel):
    itinerary: ItineraryResponse
    steps: List[ItineraryStepResponse]

    model_config = {"from_attributes": True}