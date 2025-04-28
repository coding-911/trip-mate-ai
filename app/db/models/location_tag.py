import uuid
from sqlalchemy import Column, CHAR, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class LocationTag(Base):
    __tablename__ = "location_tags"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True),
                           ForeignKey("locations.id"),
                           nullable=False)
    tag_id       = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False)
    use_yn       = Column(CHAR(1), nullable=True)
    delete_yn    = Column(CHAR(1), nullable=True)
    created_at   = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at   = Column(TIMESTAMP, server_default=func.now(),
                           onupdate=func.now(), nullable=False)
    deleted_at   = Column(TIMESTAMP, nullable=True)
