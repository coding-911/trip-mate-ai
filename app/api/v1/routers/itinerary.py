from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db


router = APIRouter(prefix="/itinerary", tags=["itinerary"])

