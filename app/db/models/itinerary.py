import uuid
from sqlalchemy import Column, Date, CHAR, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Itinerary(Base):
    __tablename__ = "itineraries"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    use_yn      = Column(CHAR(1), nullable=True)
    delete_yn   = Column(CHAR(1), nullable=True)
    created_at  = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at  = Column(TIMESTAMP, server_default=func.now(),
                         onupdate=func.now(), nullable=False)
    deleted_at  = Column(TIMESTAMP, nullable=True)
