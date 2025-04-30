import math
from sqlalchemy.orm import Session
from app.db.models.location import Location

def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # 지구 반경 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
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
        # 1) 후보 전부 로드 (하남시 데이터만 DB에 있으므로)
        candidates = (
            db.query(Location)
            .filter(Location.delete_yn == 'N', Location.use_yn == 'Y')
            .all()
        )

        # 2) 스코어링
        center_x, center_y = 127.192889, 37.563083  # 하남 미사역 기준 좌표
        tag_set = set(tags)
        scored: list[tuple[Location, float]] = []

        for loc in candidates:
            poi_tags = set(loc.category_name.split(' > ')) if loc.category_name else set()
            content_score = jaccard(tag_set, poi_tags)
            dist = haversine(center_x, center_y, float(loc.x), float(loc.y))
            dist_score = 1 / (1 + dist)
            # 태그 70%, 거리 30% 가중합
            score = content_score * 0.7 + dist_score * 0.3
            scored.append((loc, score))

        # 3) 상위 선택 및 일별 그룹화
        scored.sort(key=lambda x: x[1], reverse=True)
        total = days * per_day_count
        top_locs = [loc for loc, _ in scored[:total]]

        schedule: list[list[Location]] = []
        for d in range(days):
            start = d * per_day_count
            end = start + per_day_count
            schedule.append(top_locs[start:end])

        return schedule
