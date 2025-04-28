import uuid
from sqlalchemy import (
    Column, String, DECIMAL, Text, CHAR, TIMESTAMP, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Location(Base):
    __tablename__ = "locations"
    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kakao_place_id      = Column(String(50), nullable=True)
    name                = Column(String(255), nullable=True)
    category_group_code = Column(String(10), nullable=True)
    category_group_name = Column(String(50), nullable=True)
    category_name       = Column(String(100), nullable=True)
    phone               = Column(String(30), nullable=True)
    address_name        = Column(String(500), nullable=True)
    road_address_name   = Column(String(500), nullable=True)
    x                   = Column(DECIMAL(12,8), nullable=True)
    y                   = Column(DECIMAL(12,8), nullable=True)
    place_url           = Column(Text, nullable=True)
    use_yn              = Column(CHAR(1), nullable=True)
    delete_yn           = Column(CHAR(1), nullable=True)
    created_at          = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at          = Column(TIMESTAMP, server_default=func.now(),
                                 onupdate=func.now(), nullable=False)
    deleted_at          = Column(TIMESTAMP, nullable=True)
