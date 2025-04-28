# app/api/v1/schemas/location.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class LocationBase(BaseModel):
    kakao_place_id: Optional[str]
    name: Optional[str]
    category_group_code: Optional[str]
    category_group_name: Optional[str]
    category_name: Optional[str]
    phone: Optional[str]
    address_name: Optional[str]
    road_address_name: Optional[str]
    x: Optional[Decimal]
    y: Optional[Decimal]
    place_url: Optional[str]
    use_yn: Optional[str] = "Y"
    delete_yn: Optional[str] = "N"

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = { "from_attributes": True }
