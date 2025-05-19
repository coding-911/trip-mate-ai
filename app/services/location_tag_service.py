from sqlalchemy.orm import Session, joinedload
from app.db.models.tag import Tag
from app.db.models.location_tag import LocationTag
from app.db.models.location import Location
from uuid import UUID

class LocationTagService:
    @staticmethod
    def add_tag_to_location(location_id: UUID, tag_name: str, db: Session) -> LocationTag:
        # 1. 태그 존재 여부 확인
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name, use_yn='Y', delete_yn='N')
            db.add(tag)
            db.commit()
            db.refresh(tag)

        # 2. 장소 존재 확인
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # 3. 관계 존재 여부 확인
        location_tag = (
            db.query(LocationTag)
            .options(joinedload(LocationTag.tag))  # ✅ tag 관계 미리 로딩
            .filter_by(location_id=location_id, tag_id=tag.id)
            .first()
        )

        if not location_tag:
            location_tag = LocationTag(
                location_id=location_id,
                tag_id=tag.id,
                use_yn='Y',
                delete_yn='N',
            )
            db.add(location_tag)
            db.commit()
            db.refresh(location_tag)  # 필요하지만 관계까지는 로딩 안 함

            # 새로 만들었으면 다시 로딩 (tag 포함)
            location_tag = (
                db.query(LocationTag)
                .options(joinedload(LocationTag.tag))
                .filter_by(location_id=location_id, tag_id=tag.id)
                .first()
            )

        return location_tag
