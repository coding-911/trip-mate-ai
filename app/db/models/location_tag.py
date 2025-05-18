from typing import Optional
import uuid
from sqlalchemy import Column, CHAR, TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from app.db.base import Base
from app.db.models.tag import Tag

class LocationTag(Base):
    __tablename__ = "location_tags"
    __table_args__ = (
        UniqueConstraint("location_id", "tag_id", name="unique_location_tag"),
    )

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    tag_id       = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False)
    use_yn       = Column(CHAR(1), nullable=True)
    delete_yn    = Column(CHAR(1), nullable=True)
    created_at   = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at   = Column(TIMESTAMP, server_default=func.now(),
                           onupdate=func.now(), nullable=False)
    deleted_at   = Column(TIMESTAMP, nullable=True)

    tag: Mapped[Tag] = relationship("Tag")  #단방향

