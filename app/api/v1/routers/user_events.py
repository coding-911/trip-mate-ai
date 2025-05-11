# app/api/v1/routers/user_events.py
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_201_CREATED
from app.services.user_event_service import UserEventService

router = APIRouter(prefix="/user_event", tags=["logs"])

@router.post("/{user_id}/view/{location_id}", status_code=HTTP_201_CREATED)
def log_view(user_id: str, location_id: str):
    """
    사용자 장소 상세 페이지 view 이벤트 기록
    """
    try:
        UserEventService.view(user_id, location_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "logged", "action": "view"}

@router.post("/{user_id}/click/{location_id}", status_code=HTTP_201_CREATED)
def log_click(user_id: str, location_id: str):
    """
    사용자 클릭 이벤트 기록
    """
    try:
        UserEventService.click(user_id, location_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "logged", "action": "click"}

@router.post("/{user_id}/bookmark/{location_id}", status_code=HTTP_201_CREATED)
def log_bookmark(user_id: str, location_id: str):
    """
    사용자 bookmark 이벤트 기록
    """
    try:
        UserEventService.bookmark(user_id, location_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "logged", "action": "bookmark"}