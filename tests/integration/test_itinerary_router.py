import pytest
from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4, UUID
from datetime import datetime, date, timedelta
from app.db.models.itinerary import Itinerary
from app.db.models.itinerary_step import ItineraryStep
import os
from tests.utils.load_locations_csv import load_locations_from_csv

client = TestClient(app)

CSV_PATH = "/tmp/locations_for_test.csv"

@pytest.fixture(autouse=True)
def load_test_locations(db_session):
    if os.path.exists(CSV_PATH):
        print(f">>> 테스트용 location CSV 로딩: {CSV_PATH}")
        load_locations_from_csv(CSV_PATH, db_session)
    else:
        print(f"⚠️ 테스트용 location CSV 파일이 존재하지 않음: {CSV_PATH}")

@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def location_id(db_session):
    from app.db.models.location import Location
    loc = db_session.query(Location).first()
    return str(loc.id) if loc else str(uuid4())

@pytest.fixture
def today():
    return date.today()

def make_payload(user_id, location_id, date_, start, end, itinerary_id=None):
    payload = {
        "user_id": user_id,
        "location_id": location_id,
        "date": str(date_),
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }
    if itinerary_id:
        payload["itinerary_id"] = itinerary_id
    return payload

def test_itinerary_list_and_delete(client, user_id, location_id, today, db_session):
    # 1. 일정 2개 생성 (각각 step 2개)
    t0 = datetime.combine(today, datetime.min.time())
    t1 = t0 + timedelta(hours=1)
    t2 = t0 + timedelta(days=1)
    t3 = t2 + timedelta(hours=1)
    # 첫 번째 일정
    res1 = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, t0, t1))
    it1_id = res1.json()["itinerary_id"]
    client.post("/itinerary-step", json=make_payload(user_id, location_id, today, t1, t1+timedelta(hours=1), it1_id))
    # 두 번째 일정
    res2 = client.post("/itinerary-step", json=make_payload(user_id, location_id, today+timedelta(days=1), t2, t3))
    it2_id = res2.json()["itinerary_id"]
    client.post("/itinerary-step", json=make_payload(user_id, location_id, today+timedelta(days=1), t3, t3+timedelta(hours=1), it2_id))

    # 2. 전체 일정 조회
    list_res = client.get(f"/itinerary/user/{user_id}")
    assert list_res.status_code == 200
    data = list_res.json()
    assert len(data) == 2
    for it in data:
        assert "itinerary" in it and "steps" in it
        assert isinstance(it["steps"], list)
        assert isinstance(it["itinerary"], dict)
        assert len(it["steps"]) == 2
        for step in it["steps"]:
            assert "step_id" in step
            assert "location_id" in step
            assert "step_order" in step
            assert "date" in step
            assert "start_time" in step
            assert "end_time" in step

    # 3. 첫 번째 일정 삭제
    del_res = client.delete(f"/itinerary/{it1_id}")
    assert del_res.status_code == 200
    # 4. 다시 전체 일정 조회 (1개만 남아야 함)
    list_res2 = client.get(f"/itinerary/user/{user_id}")
    assert list_res2.status_code == 200
    data2 = list_res2.json()
    assert len(data2) == 1
    assert data2[0]["itinerary"]["id"] == it2_id
    # 5. DB에서 step도 모두 soft delete 되었는지 확인
    steps = db_session.query(ItineraryStep).filter(ItineraryStep.itinerary_id == UUID(it1_id)).all()
    assert all(step.delete_yn == 'Y' for step in steps)
    # 6. 없는 일정 삭제 시 404
    del_res2 = client.delete(f"/itinerary/{it1_id}")
    assert del_res2.status_code == 404 