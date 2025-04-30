# tests/test_recommendations_router.py
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.db.models.location import Location
import pytest

@pytest.fixture(autouse=True)
def override_db(client, db_session):
    # Override get_db dependency
    from app.db.session import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    return TestClient(app)


def test_recommend_mvp_endpoint(client, db_session, monkeypatch):
    # Create two dummy locations
    loc1 = Location(
        id=uuid4(), kakao_place_id='1', name='L1', x=127.215, y=37.540,
        category_group_code='CG', category_group_name='CGN',
        category_name='카페', use_yn='Y', delete_yn='N'
    )
    loc2 = Location(
        id=uuid4(), kakao_place_id='2', name='L2', x=127.215, y=37.540,
        category_group_code='CG', category_group_name='CGN',
        category_name='공원', use_yn='Y', delete_yn='N'
    )
    db_session.add_all([loc1, loc2])
    db_session.commit()

    # Monkeypatch service
    from app.services.recommendation_service import RecommendationService
    monkeypatch.setattr(RecommendationService, 'recommend_mvp',
                        lambda tags, days, per_day_count, db: [[loc1, loc2]])

    response = client.post('/recommendations/mvp', json={
        'tags': ['카페'],
        'days': 1,
        'per_day_count': 2
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0][0]['id'] == str(loc1.id)
    assert data[0][1]['id'] == str(loc2.id)
