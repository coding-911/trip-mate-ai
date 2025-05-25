import traceback
from elasticsearch import Elasticsearch
from app.core.config import settings
from datetime import datetime, timezone

# ES 호스트는 .env의 ELASTICSEARCH_HOSTS="http://elasticsearch:9200" 등을 사용
es = Elasticsearch(settings.ELASTICSEARCH_HOSTS)

class UserEventService:
    INDEX = "user-events"

    @classmethod
    def log_event(
        cls,
        user_id:     str,
        location_id: str,
        action:      str,
    ):
        doc = {
            "user_id":     user_id,
            "location_id": location_id,
            "action":      action,
            "timestamp":   datetime.now(timezone.utc).isoformat(),        # ES가 자동으로 현재 시각을 할당
        }
        try:
            res = es.index(index=cls.INDEX, document=doc)
            print(">>> Elasticsearch response:", res)
            return res
        except Exception as e:
            print(">>> Elasticsearch error:")
            traceback.print_exc()
            raise

    @classmethod
    def view(cls, user_id: str, location_id: str):
        return cls.log_event(user_id, location_id, action="view")

    @classmethod
    def click(cls, user_id: str, location_id: str):
        return cls.log_event(user_id, location_id, action="click")

    @classmethod
    def bookmark(cls, user_id: str, location_id: str):
        return cls.log_event(user_id, location_id, action="bookmark")
