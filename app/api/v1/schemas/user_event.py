# app/api/v1/schemas/user_event.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional

MAX_COMMENT_LENGTH = 500  # DB VARCHAR(500)

class RatingRequest(BaseModel):
    value: float = Field(
        ...,
        ge=0.0,
        le=5.0,
        description="0.0~5.0 사이의 평점 (0.5 단위)"
    )
    comment: Optional[str] = Field(
        None,
        max_length=MAX_COMMENT_LENGTH,
        description=f"사용자 코멘트 (최대 {MAX_COMMENT_LENGTH}자)"
    )

    @field_validator("value")
    def must_be_half_step(cls, v: float) -> float:
        if not (v * 2).is_integer():
            raise ValueError("value는 0.5 단위여야 합니다.")
        return v

    @field_validator("comment")
    def comment_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > MAX_COMMENT_LENGTH:
            raise ValueError(f"최대 {MAX_COMMENT_LENGTH}자까지 입력 가능합니다.")
        return v

    model_config = {"from_attributes": True}
