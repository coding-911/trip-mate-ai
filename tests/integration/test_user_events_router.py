# tests/integration/test_user_events_router.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.user_event_service import UserEventService

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_log_event(monkeypatch):
    def fake_log_event(user_id, location_id, action, value=1.0):
        return {"result": "created"}
    monkeypatch.setattr(UserEventService, "log_event", fake_log_event)

@pytest.mark.parametrize("action", ["view", "click", "bookmark"])
def test_user_event_endpoints(action):
    url = f"/users/alice/{action}/loc-1234"
    resp = client.post(url)
    assert resp.status_code == 201
    assert resp.json() == {"status": "logged", "action": action}
