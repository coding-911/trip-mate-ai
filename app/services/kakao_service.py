import httpx
import math
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.location import Location
from sqlalchemy.exc import SQLAlchemyError

class KakaoService:
    """
    Kakao Local API를 사용해 키워드 기반 장소 검색 및 DB 저장을 수행합니다.
    단일 호출 최대 개수 제한은 무료 요금제 기준 15건이며, 그 이상 요청 시 페이지네이션으로 처리합니다.
    """
    MAX_PAGE_SIZE = 15
    BASE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
    HEADERS = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}

    @classmethod
    def search_and_save(cls, keyword: str, db: Session, total_count: int):
        # 1) 입력 방어
        keyword = keyword.strip()
        if not keyword:
            return []

        saved_locations = []
        per_page = cls.MAX_PAGE_SIZE
        total_pages = math.ceil(total_count / per_page)

        # 2) 페이지별 호출
        for page in range(1, total_pages + 1):
            size = min(per_page, total_count - len(saved_locations))
            params = {"query": keyword, "size": size, "page": page}

            resp = httpx.get(cls.BASE_URL, headers=cls.HEADERS, params=params, timeout=5.0)
            if resp.status_code != 200:
                # Kakao API 에러 메시지 포함하여 예외 발생
                raise RuntimeError(f"Kakao API error ({resp.status_code}): {resp.text}")

            documents = resp.json().get("documents", [])
            if not documents:
                break

            # 3) DB 저장
            for doc in documents:
                kakao_id = doc.get("id")
                existing = db.query(Location).filter(Location.kakao_place_id == kakao_id).first()
                if existing:
                    saved_locations.append(existing)
                    continue

                loc = Location(
                    kakao_place_id      = kakao_id,
                    name                = doc.get("place_name"),
                    category_group_code = doc.get("category_group_code"),
                    category_group_name = doc.get("category_group_name"),
                    category_name       = doc.get("category_name"),
                    phone               = doc.get("phone"),
                    address_name        = doc.get("address_name"),
                    road_address_name   = doc.get("road_address_name"),
                    x                   = doc.get("x"),
                    y                   = doc.get("y"),
                    place_url           = doc.get("place_url"),
                    use_yn              = 'Y',
                    delete_yn           = 'N',
                )
                try:
                    db.add(loc)
                    db.commit()
                    db.refresh(loc)
                    saved_locations.append(loc)
                except SQLAlchemyError:
                    db.rollback()

            # 4) 요청 개수가 채워졌으면 종료
            if len(saved_locations) >= total_count:
                break

        return saved_locations
