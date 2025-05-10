from elasticsearch import Elasticsearch
from app.core.config import settings
from datetime import datetime, timezone

# ES 호스트는 .env의 ELASTICSEARCH_HOSTS="http://elasticsearch:9200" 등을 사용
es = Elasticsearch(settings.ELASTICSEARCH_HOSTS)

class UserEventService:
    INDEX = "user-logs"

    @classmethod
    def log_event(
        cls,
        user_id:     str,
        location_id: str,
        action:      str,
        value:       float = 1.0,
    ):
        doc = {
            "user_id":     user_id,
            "location_id": location_id,
            "action":      action,
            "value":       value,
            "timestamp":   datetime.now(timezone.utc).isoformat(),        # ES가 자동으로 현재 시각을 할당
        }
        return es.index(index=cls.INDEX, document=doc)

    @classmethod
    def view(cls, user_id: str, location_id: str):
        return cls.log_event(user_id, location_id, action="view")

    @classmethod
    def click(cls, user_id: str, location_id: str):
        return cls.log_event(user_id, location_id, action="click")

    @classmethod
    def bookmark(cls, user_id: str, location_id: str):
        return cls.log_event(user_id, location_id, action="bookmark")
