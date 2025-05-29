import uuid
from sqlalchemy import (
    Column, Integer, Date, TIMESTAMP, Text, CHAR, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class ItineraryStep(Base):
    __tablename__ = "itinerary_steps"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True),
                           ForeignKey("itineraries.id"),
                           nullable=False)
    location_id     = Column(UUID(as_uuid=True),
                           ForeignKey("locations.id"),
                           nullable=False)
    step_order   = Column(Integer, nullable=False)
    date         = Column(Date, nullable=False)
    start_time   = Column(TIMESTAMP, nullable=False)
    end_time     = Column(TIMESTAMP, nullable=False)
    comment      = Column(Text, nullable=True)
    use_yn       = Column(CHAR(1), nullable=True)
    delete_yn    = Column(CHAR(1), nullable=True)
    created_at   = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at   = Column(TIMESTAMP, server_default=func.now(),
                           onupdate=func.now(), nullable=False)
    deleted_at   = Column(TIMESTAMP, nullable=True)
