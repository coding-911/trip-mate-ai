import math
import json
import redis
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from lightfm import LightFM
from uuid import UUID 

from app.db.models.location import Location
from app.batch.location.recommendation.load_model import load_trained_model, load_user_interactions
from app.core.config import settings



# Redis 클라이언트
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

def haversine(lon1, lat1, lon2, lat2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

class RecommendationService:
    @classmethod
    def recommend_mvp(
        cls,
        tags: list[str],
        days: int,
        per_day_count: int,
        db: Session
    ) -> list[list[Location]]:
        candidates = (
            db.query(Location)
            .filter(Location.delete_yn == 'N', Location.use_yn == 'Y')
            .all()
        )

        center_x, center_y = 127.192889, 37.563083  # 하남 미사역
        tag_set = set(tags)
        scored: list[tuple[Location, float]] = []

        for loc in candidates:
            poi_tags = set(loc.category_name.split(' > ')) if loc.category_name else set()
            content_score = jaccard(tag_set, poi_tags)
            dist = haversine(center_x, center_y, float(loc.x), float(loc.y))
            dist_score = 1 / (1 + dist)
            score = content_score * 0.7 + dist_score * 0.3
            scored.append((loc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        total = days * per_day_count
        top_locs = [loc for loc, _ in scored[:total]]

        schedule = []
        for d in range(days):
            start = d * per_day_count
            end = start + per_day_count
            schedule.append(top_locs[start:end])

        return schedule

    @classmethod
    def recommend_model(
        cls,
        user_id: str,
        days: int,
        per_day_count: int,
        db: Session,
        fallback_tags: list[str] = None
    ) -> list[list[Location]]:
        model: LightFM
        user_map: dict
        item_map: dict

        model, user_map, item_map, item_features  = load_trained_model()
        user_idx = user_map.get(user_id)

        if user_idx is None:
            if fallback_tags:
                print(f">>> 사용자 로그 없음 → MVP 방식으로 대체 추천")
                return cls.recommend_mvp(fallback_tags, days, per_day_count, db)
            else:
                return []

        scores = model.predict(
            user_ids=user_idx,
            item_ids=list(range(len(item_map))),
            item_features=item_features
        )
        top_items = sorted(zip(range(len(scores)), scores), key=lambda x: x[1], reverse=True)

        total = days * per_day_count
        top_location_ids = [list(item_map.keys())[i] for i, _ in top_items[:total]]
        top_location_ids = [UUID(loc_id) for loc_id in top_location_ids]
        print(f">>> total items in model: {len(item_map)}")
        print(f">>> top_location_ids: {top_location_ids}")

        locations = db.query(Location).filter(Location.id.in_(top_location_ids)).all()
        id_to_loc = {str(loc.id): loc for loc in locations}
        sorted_locs = [id_to_loc[str(loc_id)] for loc_id in top_location_ids if str(loc_id) in id_to_loc]
        print(f">>> model top ids: {top_location_ids}")
        print(f">>> DB에 실제 존재하는 id: {id_to_loc}")

        schedule = []
        for d in range(days):
            start = d * per_day_count
            end = start + per_day_count
            schedule.append(sorted_locs[start:end])

        return schedule

    @classmethod
    def recommend(
        cls,
        method: str,
        user_id: str,
        tags: list[str],
        days: int,
        per_day_count: int,
        db: Session
    ) -> list[list[Location]]:
        if method == "mvp":
            return cls.recommend_mvp(tags, days, per_day_count, db)
        elif method == "model":
            return cls.recommend_model(user_id, days, per_day_count, db, fallback_tags=tags)
        elif method == "auto":
            user_map, _, _ = load_user_interactions()
            if user_id in user_map:
                print("recommend_model")
                return cls.recommend_model(user_id, days, per_day_count, db, fallback_tags=tags)
            else:
                print("recommend_mvp")
                return cls.recommend_mvp(tags, days, per_day_count, db)
        else:
            raise ValueError(f"Unknown recommendation method: {method}")

    @classmethod
    def recommend_with_cache(
        cls,
        method: str,
        user_id: str,
        tags: list[str],
        days: int,
        per_day_count: int,
        db: Session
    ) -> list[list[Location]]:
        model_version = datetime.now().strftime("%Y%m%d")
        key = f"recommend:{method}:{user_id}:{model_version}"

        if redis_client.exists(key):
            location_ids = json.loads(redis_client.get(key))
        else:
            results = cls.recommend(method, user_id, tags, days, per_day_count, db)
            location_ids = [[str(loc.id) for loc in day] for day in results]

            # TTL: 다음날 새벽 1시까지
            now = datetime.now()
            expire_at = now.replace(hour=1, minute=0, second=0, microsecond=0)
            if now.hour >= 1:
                expire_at += timedelta(days=1)
            ttl = int((expire_at - now).total_seconds())

            redis_client.setex(key, ttl, json.dumps(location_ids))

        flat_ids = [id for day in location_ids for id in day]
        locations = db.query(Location).filter(Location.id.in_(flat_ids)).all()
        id_map = {str(loc.id): loc for loc in locations}
        return [[id_map[loc_id] for loc_id in day if loc_id in id_map] for day in location_ids]
