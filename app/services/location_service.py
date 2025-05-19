# app/services/location_service.py
from sqlalchemy.orm import Session
from app.db.models.location import Location

class LocationService:
    @staticmethod
    def get_active_locations(db: Session):
        return db.query(Location).filter(
            Location.use_yn == 'Y',
            Location.delete_yn == 'N'
        ).all()
