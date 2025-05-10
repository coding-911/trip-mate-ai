# tests/integration/test_user_event_router.py
import pytest
from elasticsearch import Elasticsearch
from app.services import user_event_service
from uuid import uuid4


@pytest.mark.parametrize("action", ["view", "click", "bookmark"])
def test_user_event_endpoint_logs_to_es(es_test_client, action):
    user_id = f"user-{uuid4()}"
    location_id = f"loc-{uuid4()}"

    url = f"/user_event/{user_id}/{action}/{location_id}"
    response = es_test_client.post(url)

    assert response.status_code == 201
    assert response.json() == {"status": "logged", "action": action}

    # Elasticsearch 로그 확인
    es: Elasticsearch = user_event_service.es
    es.indices.refresh(index=user_event_service.UserEventService.INDEX)

    result = es.search(
        index=user_event_service.UserEventService.INDEX,
        query={
            "bool": {
                "must": [
                    {"match": {"user_id": user_id}},
                    {"match": {"location_id": location_id}},
                    {"match": {"action": action}}
                ]
            }
        }
    )

    hits = result["hits"]["hits"]
    assert len(hits) > 0
    doc = hits[0]["_source"]
    assert doc["user_id"] == user_id
    assert doc["location_id"] == location_id
    assert doc["action"] == action
    assert "timestamp" in doc
