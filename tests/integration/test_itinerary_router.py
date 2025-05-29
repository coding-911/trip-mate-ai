import pytest
from uuid import uuid4
from datetime import datetime, date, timedelta
from tests.utils.load_locations_csv import load_locations_from_csv
import os

CSV_PATH = "/tmp/locations_for_test.csv"

@pytest.fixture(autouse=True)
def load_test_locations(db_session):
    if os.path.exists(CSV_PATH):
        print(f">>> 테스트용 location CSV 로딩: {CSV_PATH}")    
        load_locations_from_csv(CSV_PATH, db_session)
    else:
        print(f"⚠️ 테스트용 location CSV 파일이 존재하지 않음: {CSV_PATH}")

# client fixture는 conftest.py에서 import해서 사용
from tests.conftest import client

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

@pytest.fixture
def tomorrow():
    return date.today() + timedelta(days=1)


def make_payload(user_id, location_id, date_, start, end):
    return {
        "user_id": user_id,
        "location_id": location_id,
        "date": str(date_),
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }

def test_create_first_itinerary_and_step(client, user_id, location_id, today):
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(hours=2)
    payload = make_payload(user_id, location_id, today, start, end)
    res = client.post("/itinerary/step", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["step_order"] == 0
    assert data["date"] == str(today)
    assert data["location_id"] == location_id


def test_add_multiple_steps_time_order(client, user_id, today):
    locs = [str(uuid4()) for _ in range(3)]
    times = [datetime.combine(today, datetime.min.time()) + timedelta(hours=i*2) for i in range(3)]
    step_ids = []
    for i in range(3):
        payload = make_payload(user_id, locs[i], today, times[i], times[i]+timedelta(hours=1))
        res = client.post("/itinerary/step", json=payload)
        assert res.status_code == 200
        data = res.json()
        step_ids.append(data["step_id"])
        assert data["step_order"] == i
    assert len(set(step_ids)) == 3


def test_insert_step_earlier_time(client, user_id, today):
    locs = [str(uuid4()) for _ in range(3)]
    t0 = datetime.combine(today, datetime.min.time())
    t1 = t0 + timedelta(hours=2)
    t2 = t0 + timedelta(hours=1)
    client.post("/itinerary/step", json=make_payload(user_id, locs[0], today, t0, t0+timedelta(hours=1)))
    client.post("/itinerary/step", json=make_payload(user_id, locs[1], today, t1, t1+timedelta(hours=1)))
    res = client.post("/itinerary/step", json=make_payload(user_id, locs[2], today, t2, t2+timedelta(hours=1)))
    assert res.status_code == 200
    data = res.json()
    assert data["step_order"] == 1


def test_create_itinerary_different_dates(client, user_id, location_id, today, tomorrow):
    start1 = datetime.combine(today, datetime.min.time())
    end1 = start1 + timedelta(hours=1)
    start2 = datetime.combine(tomorrow, datetime.min.time())
    end2 = start2 + timedelta(hours=1)
    res1 = client.post("/itinerary/step", json=make_payload(user_id, location_id, today, start1, end1))
    res2 = client.post("/itinerary/step", json=make_payload(user_id, location_id, tomorrow, start2, end2))
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json()["date"] == str(today)
    assert res2.json()["date"] == str(tomorrow) 