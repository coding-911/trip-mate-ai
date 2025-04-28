from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TagBase(BaseModel):
    name: str
    use_yn: Optional[str] = "Y"
    delete_yn: Optional[str] = "N"

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = { "from_attributes": True }
