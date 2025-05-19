# app/api/v1/schemas/location_tag.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class LocationTagBase(BaseModel):
    location_id: UUID
    tag_id: UUID
    use_yn: Optional[str] = "Y"
    delete_yn: Optional[str] = "N"

class LocationTagResponse(BaseModel):
    location_id: UUID
    tag_id: UUID
    tag_name: str

    model_config = {"from_attributes": True}