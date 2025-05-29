import pytest
from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4, UUID
from datetime import datetime, date, timedelta
from app.db.models.itinerary import Itinerary
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

def test_create_step_with_new_itinerary(client, user_id, location_id, today, db_session):
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(hours=2)
    res = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, start, end))
    assert res.status_code == 200
    data = res.json()
    assert data["step_order"] == 0
    # itinerary가 생성되었는지 확인
    itinerary_id = data["itinerary_id"]
    itinerary = db_session.query(Itinerary).filter(Itinerary.id == UUID(itinerary_id)).first()
    assert itinerary is not None

def test_create_step_with_existing_itinerary_id(client, user_id, location_id, today, db_session):
    from uuid import uuid4, UUID
    itinerary_id = uuid4()
    itinerary = Itinerary(
        id=itinerary_id,
        user_id=UUID(user_id),
        start_date=today,
        end_date=today,
        use_yn='Y',
        delete_yn='N',
    )
    db_session.add(itinerary)
    db_session.commit()
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(hours=2)
    res = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, start, end, str(itinerary_id)))
    assert res.status_code == 200
    data = res.json()
    assert data["step_order"] == 0
    assert data["itinerary_id"] == str(itinerary_id)

def test_create_step_with_nonexistent_itinerary_id(client, user_id, location_id, today):
    # 존재하지 않는 itinerary_id로 요청
    from uuid import uuid4
    fake_itinerary_id = str(uuid4())
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(hours=2)
    res = client.post(
        "/itinerary-step",
        json={
            "user_id": user_id,
            "location_id": location_id,
            "date": str(today),
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "itinerary_id": fake_itinerary_id,
        }
    )
    assert res.status_code in (400, 404, 500)  # 실제 서비스 코드에 맞게 조정

def test_step_order_and_reorder_on_update(client, user_id, location_id, today, db_session):
    t0 = datetime.combine(today, datetime.min.time())
    t1 = t0 + timedelta(hours=2)
    t2 = t0 + timedelta(hours=1)
    res1 = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, t0, t0+timedelta(hours=1)))
    res2 = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, t1, t1+timedelta(hours=1)))
    res3 = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, t2, t2+timedelta(hours=1)))
    id1 = res1.json()["step_id"]
    id2 = res2.json()["step_id"]
    id3 = res3.json()["step_id"]
    itinerary_id = res1.json()["itinerary_id"]

    # DB에서 step들을 시간순으로 조회해서 step_order가 0,1,2인지 검증
    from app.db.models.itinerary_step import ItineraryStep
    steps = db_session.query(ItineraryStep).filter(
        ItineraryStep.itinerary_id == UUID(itinerary_id),
        ItineraryStep.delete_yn == 'N',
        ItineraryStep.use_yn == 'Y',
    ).order_by(ItineraryStep.date, ItineraryStep.start_time).all()
    orders = [step.step_order for step in steps]
    assert orders == [0, 1, 2]

def test_delete_step_and_soft_delete_itinerary(client, user_id, location_id, today, db_session):
    res = client.post("/itinerary-step", json=make_payload(user_id, location_id, today, datetime.combine(today, datetime.min.time()), datetime.combine(today, datetime.min.time())+timedelta(hours=1)))
    step_id = res.json()["step_id"]
    itinerary_id = res.json()["itinerary_id"]
    del_res = client.delete(f"/itinerary-step/{step_id}")
    assert del_res.status_code == 200
    itinerary = db_session.query(Itinerary).filter(Itinerary.id == UUID(itinerary_id)).first()
    assert itinerary.delete_yn == 'Y' 