import pytest
from app.services.user_event_service import UserEventService, es

class DummyResponse(dict):
    def __init__(self, result="created"):
        super().__init__(result=result)


def test_log_event_success(monkeypatch):
    captured = {}
    def fake_index(index: str, document: dict):
        captured['index'] = index
        captured['document'] = document
        return DummyResponse("created")

    monkeypatch.setattr(es, "index", fake_index)

    res = UserEventService.log_event(
        user_id="user-1",
        location_id="loc-42",
        action="view",
        value=2.5
    )

    assert isinstance(res, dict)
    assert res["result"] == "created"
    assert captured["index"] == UserEventService.INDEX
    doc = captured["document"]
    assert doc["user_id"]     == "user-1"
    assert doc["location_id"] == "loc-42"
    assert doc["action"]      == "view"
    assert doc["value"]       == 2.5
    assert doc["timestamp"]   == "now"


def test_log_event_error_propagates(monkeypatch):
    def fake_index_fail(index, document):
        raise RuntimeError("ES down")

    monkeypatch.setattr(es, "index", fake_index_fail)

    with pytest.raises(RuntimeError) as exc:
        UserEventService.log_event("u", "l", "click")
    assert "ES down" in str(exc.value)


@pytest.mark.parametrize("method,action", [
    ("view", "view"),
    ("click", "click"),
    ("bookmark", "bookmark"),
])
def test_action_wrappers_call_log_event(monkeypatch, method, action):
    called = {}
    def fake_log_event(*args, **kwargs):
        # args = (user_id, location_id)
        # kwargs contains 'action' and optional 'value'
        called['params'] = (
            args[0],           # user_id
            args[1],           # location_id
            kwargs.get('action'),
            kwargs.get('value', 1.0)
        )
        return {"result": "created"}

    monkeypatch.setattr(UserEventService, "log_event", fake_log_event)

    func = getattr(UserEventService, method)
    res = func("u123", "loc999")
    assert res == {"result": "created"}
    assert called['params'] == ("u123", "loc999", action, 1.0)