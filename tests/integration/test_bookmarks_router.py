import pytest
from uuid import UUID
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.core.dependencies.auth import get_current_user
from app.db.models.user import User
from app.db.models.location import Location
from app.db.models.bookmark import Bookmark


def create_test_user(db):
    u = User(
        email="test@example.com",
        password_hash="hash",
        name="testuser",
        year_of_birth=1990,
        country_code="KR",
        use_yn='Y',
        delete_yn='N'
    )
    db.add(u); db.commit(); db.refresh(u)
    return u

def create_test_location(db):
    loc = Location(name="T1", category_name="테스트", x=1.0, y=1.0, use_yn='Y', delete_yn='N')
    db.add(loc); db.commit(); db.refresh(loc)
    return loc


# ES 포함된 인증 클라이언트
@pytest.fixture
def auth_es_client(es_test_client: TestClient, db_session):
    """
    Elasticsearch가 포함된 클라이언트에 인증 유저를 주입한 버전.
    """
    user = create_test_user(db_session)
    token = f"testtoken-{user.id}"

    def fake_current_user():
        return user

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = fake_current_user

    es_test_client.headers.update({"Authorization": f"Bearer {token}"})
    return es_test_client


def test_create_bookmark_endpoint(auth_es_client, db_session):
    loc = create_test_location(db_session)

    resp = auth_es_client.post(
        "/bookmark",
        json={"location_id": str(loc.id)},
    )
    print("API_RESPONSE:", resp.status_code, resp.text)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data

    bm_id = UUID(data["id"])
    bm = db_session.query(Bookmark).filter_by(id=bm_id).first()
    assert bm is not None
    assert bm.location_id == loc.id


def test_list_bookmarks_endpoint(auth_es_client, db_session):
    loc1 = create_test_location(db_session)
    loc2 = create_test_location(db_session)

    auth_es_client.post("/bookmark", json={"location_id": str(loc1.id)})
    auth_es_client.post("/bookmark", json={"location_id": str(loc2.id)})

    resp = auth_es_client.get("/bookmark")
    assert resp.status_code == 200
    arr = resp.json()
    assert any(item["id"] == str(loc1.id) for item in arr)
    assert any(item["id"] == str(loc2.id) for item in arr)


def test_delete_bookmark_endpoint(auth_es_client, db_session):
    loc = create_test_location(db_session)
    create = auth_es_client.post("/bookmark", json={"location_id": str(loc.id)})
    bm_id = create.json()["id"]

    resp = auth_es_client.delete(f"/bookmark/{bm_id}")
    assert resp.status_code == 204

    bm = db_session.query(Bookmark).get(UUID(bm_id))
    assert bm.delete_yn == 'Y'
    assert bm.use_yn    == 'N'
