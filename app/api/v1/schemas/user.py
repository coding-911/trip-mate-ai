# app/api/v1/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    year_of_birth: Optional[int] = None
    country_code: Optional[str] = None

class UserRead(UserBase):
    id: UUID
    use_yn: str
    delete_yn: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # ↓ v2 방식의 ORM 호환 설정
    model_config = ConfigDict(from_attributes=True)