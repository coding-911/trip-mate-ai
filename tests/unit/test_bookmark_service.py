import pytest
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.services.bookmark_service import BookmarkService
from app.db.models.bookmark import UserBookmark
from app.services.user_event_service import UserEventService

class DummyEvent:
    def __init__(self):
        self.calls = []

    def index(self, index, document):
        self.calls.append((index, document))
        return {"result": "created"}

@pytest.fixture(autouse=True)
def patch_es(monkeypatch):
    dummy = DummyEvent()
    # Elasticsearch client 대체
    monkeypatch.setattr(UserEventService, "log_event", lambda *args, **kwargs: dummy.calls.append((args, kwargs)))
    return dummy

def test_add_bookmark_creates_new(db_session: Session, patch_es: DummyEvent):
    user_id = uuid4()
    loc_id  = uuid4()

    bm = BookmarkService.add_bookmark(db_session, str(user_id), str(loc_id))
    assert isinstance(bm, UserBookmark)
    assert bm.user_id == user_id
    assert bm.location_id == loc_id

    # 이벤트가 1회 기록되었는지
    assert len(patch_es.calls) == 1
    args, kwargs = patch_es.calls[0]
    assert args[0] == user_id and args[1] == loc_id and kwargs["action"] == "bookmark"

def test_add_bookmark_idempotent(db_session: Session, patch_es: DummyEvent):
    user_id = uuid4()
    loc_id  = uuid4()

    bm1 = BookmarkService.add_bookmark(db_session, str(user_id), str(loc_id))
    bm2 = BookmarkService.add_bookmark(db_session, str(user_id), str(loc_id))

    # 같은 객체 반환
    assert bm1.id == bm2.id
    # 이벤트는 최초 1회만
    assert len(patch_es.calls) == 1

def test_remove_bookmark_soft_delete(db_session: Session, patch_es: DummyEvent):
    user_id = uuid4()
    loc_id  = uuid4()
    bm = BookmarkService.add_bookmark(db_session, str(user_id), str(loc_id))
    patch_es.calls.clear()

    # 삭제 호출
    BookmarkService.remove_bookmark(db_session, str(user_id), str(bm.id))

    # soft delete 필드 확인
    db_session.refresh(bm)
    assert bm.delete_yn == 'Y'
    assert bm.use_yn    == 'N'
    assert bm.deleted_at is not None

    # 이벤트 로그(bookmark_cancel) 확인
    assert len(patch_es.calls) == 1
    args, kwargs = patch_es.calls[0]
    assert kwargs["action"] == "bookmark_cancel"
