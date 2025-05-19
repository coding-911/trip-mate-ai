import httpx
import math
from sqlalchemy.orm import Session
from app.core.config import settings
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.location import Location
from app.db.models.location_tag import LocationTag
from app.db.models.tag import Tag

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
        saved_ids = set()  # 여기서 중복 방지를 위한 id 집합 관리
        per_page = cls.MAX_PAGE_SIZE
        total_pages = math.ceil(total_count / per_page)

        for page in range(1, total_pages + 1):
            size = min(per_page, total_count - len(saved_locations))
            params = {"query": keyword, "size": size, "page": page}

            resp = httpx.get(cls.BASE_URL, headers=cls.HEADERS, params=params, timeout=5.0)
            if resp.status_code != 200:
                raise RuntimeError(f"Kakao API error ({resp.status_code}): {resp.text}")

            documents = resp.json().get("documents", [])
            if not documents:
                break

            for doc in documents:
                kakao_id = doc.get("id")
                if not kakao_id or kakao_id in saved_ids:
                    continue  # 현재 요청 API에서 이미 수집한 적 있는 ID는 건너뛰기

                existing = db.query(Location).filter(Location.kakao_place_id == kakao_id).first()
                if existing:
                    saved_locations.append(existing)
                    saved_ids.add(kakao_id)
                    continue  # DB에 이미 저장된 ID는 건너뛰기

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
                    saved_ids.add(kakao_id)

                    # 태그 매핑 시작
                    tag_name = doc.get("category_group_name")
                    if tag_name:
                        tag = db.query(Tag).filter(Tag.name == tag_name).first()
                        if not tag:
                            tag = Tag(name=tag_name, use_yn='Y', delete_yn='N')
                            db.add(tag)
                            db.commit()
                            db.refresh(tag)

                        # 중복 연결 방지
                        exists = db.query(LocationTag).filter_by(location_id=loc.id, tag_id=tag.id).first()
                        if not exists:
                            location_tag = LocationTag(
                                location_id=loc.id,
                                tag_id=tag.id,
                                use_yn='Y',
                                delete_yn='N',
                            )
                            db.add(location_tag)
                            db.commit()

                except SQLAlchemyError as e:
                    db.rollback()
                    print(f"[DB ERROR] failed to insert location or tag: {e}")

            if len(saved_locations) >= total_count:
                break


        return saved_locations
