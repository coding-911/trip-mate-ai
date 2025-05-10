# app/api/v1/schemas/bookmark.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class BookmarkCreate(BaseModel):
    """즐겨찾기 생성 요청 스키마"""
    location_id: UUID = Field(
        ..., description="즐겨찾기할 장소의 UUID"
    )

    model_config = {"from_attributes": True}

    @field_validator("location_id")
    def validate_location_id(cls, v: UUID) -> UUID:
        if not isinstance(v, UUID):
            raise ValueError("location_id는 UUID여야 합니다.")
        return v


class BookmarkResponse(BaseModel):
    """즐겨찾기 응답 스키마"""
    id: UUID = Field(..., description="즐겨찾기 고유 ID")
    user_id: UUID = Field(..., description="해당 즐겨찾기 생성한 사용자 ID")
    location_id: UUID = Field(..., description="즐겨찾기된 장소 ID")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="수정 시각")
    deleted_at: Optional[datetime] = Field(None, description="삭제 시각 (soft delete)")

    model_config = {"from_attributes": True}