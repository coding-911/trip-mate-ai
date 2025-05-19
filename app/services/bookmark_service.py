from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from app.db.models.bookmark import Bookmark
from app.services.user_event_service import UserEventService
from app.db.models.location import Location

class BookmarkService:
    @staticmethod
    def add_bookmark(db: Session, user_id, location_id) -> Bookmark:
        # str → UUID 변환
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(location_id, str):
            location_id = UUID(location_id)

        # 중복 검사
        existing = (
            db.query(Bookmark)
              .filter(
                  Bookmark.user_id == user_id,
                  Bookmark.location_id == location_id,
                  Bookmark.delete_yn == 'N',
                  Bookmark.use_yn    == 'Y',
              )
              .first()
        )
        if existing:
            return existing

        # 반드시 키워드 인자로 넘겨야 함
        bm = Bookmark(user_id=user_id, location_id=location_id)
        db.add(bm)
        db.commit()
        db.refresh(bm)

        UserEventService.log_event(user_id, location_id, action="bookmark")
        return bm

    @staticmethod
    def get_bookmarked_locations(db: Session, user_id) -> list[Location]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        bookmarks = (
            db.query(Bookmark)
              .filter(
                  Bookmark.user_id == user_id,
                  Bookmark.delete_yn == 'N',
                  Bookmark.use_yn    == 'Y',
              )
              .all()
        )
        location_ids = [bm.location_id for bm in bookmarks]
        return (
            db.query(Location)
              .filter(
                  Location.id.in_(location_ids),
                  Location.delete_yn == 'N',
                  Location.use_yn    == 'Y',
              )
              .all()
        )

    @staticmethod
    def remove_bookmark(db: Session, user_id, bookmark_id) -> None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(bookmark_id, str):
            bookmark_id = UUID(bookmark_id)

        bm = (
            db.query(Bookmark)
              .filter(
                  Bookmark.id        == bookmark_id,
                  Bookmark.user_id   == user_id,
                  Bookmark.delete_yn == 'N',
                  Bookmark.use_yn    == 'Y',
              )
              .first()
        )
        if not bm:
            return

        bm.delete_yn  = 'Y'
        bm.use_yn     = 'N'
        bm.deleted_at = func.now()
        db.commit()

        UserEventService.log_event(user_id, bm.location_id, action="bookmark_cancel")
