from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.bookmark_service import BookmarkService
from app.api.v1.schemas.bookmark import BookmarkCreate, BookmarkResponse
from app.api.v1.schemas.location import LocationResponse
from app.core.dependencies.auth import get_current_user

router = APIRouter(prefix="/bookmark", tags=["bookmarks"])

@router.post("", status_code=HTTP_201_CREATED, response_model=BookmarkResponse)
def create_bookmark(
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """현재 로그인한 사용자의 즐겨찾기 생성"""
    try:
        bm = BookmarkService.add_bookmark(
            db,
            current_user.id,
            payload.location_id,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return bm

@router.get("", response_model=list[LocationResponse])
def list_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """현재 로그인한 사용자의 즐겨찾기한 장소 목록 조회"""
    try:
        return BookmarkService.get_bookmarked_locations(
            db,
            current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{bookmark_id}", status_code=HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """현재 로그인한 사용자의 즐겨찾기 삭제"""
    try:
        BookmarkService.remove_bookmark(
            db,
            current_user.id,
            bookmark_id,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return
