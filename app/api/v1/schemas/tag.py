from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# 태그 자체를 생성/수정할 때 사용
class TagBase(BaseModel):
    name: str
    use_yn: Optional[str] = "Y"
    delete_yn: Optional[str] = "N"


# 장소에 태그를 연결할 때 사용하는 요청 모델
class TagNameRequest(BaseModel):
    tag_name: str


# 태그 생성 요청 (ex: 관리자 전용 API 등)
class TagCreate(TagBase):
    pass


# 태그 수정 요청
class TagUpdate(BaseModel):
    name: Optional[str] = None
    use_yn: Optional[str] = None
    delete_yn: Optional[str] = None


# 태그 응답 모델
class TagResponse(BaseModel):
    id: UUID
    name: str

    model_config = { "from_attributes": True }