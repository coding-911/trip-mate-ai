# tests/unit/test_user_event_service.py
import pytest
from app.services.user_event_service import UserEventService


@pytest.mark.parametrize("method, action", [
    ("view", "view"),
    ("click", "click"),
    ("bookmark", "bookmark"),
])
def test_action_wrapper_calls_log_event(monkeypatch, method, action):
    called = {}

    def fake_log_event(user_id, location_id, *, action, value=1.0):
        called.update({
            "user_id": user_id,
            "location_id": location_id,
            "action": action,
            "value": value,
        })
        return {"result": "created"}

    monkeypatch.setattr(UserEventService, "log_event", fake_log_event)

    func = getattr(UserEventService, method)
    result = func("user-123", "loc-456")

    assert result["result"] == "created"
    assert called["user_id"] == "user-123"
    assert called["location_id"] == "loc-456"
    assert called["action"] == action
    assert called["value"] == 1.0
