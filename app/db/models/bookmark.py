import uuid
from sqlalchemy import Column, CHAR, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id         = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    location_id= Column(PGUUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    use_yn     = Column(CHAR(1), nullable=False, default='Y')
    delete_yn  = Column(CHAR(1), nullable=False, default='N')
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)