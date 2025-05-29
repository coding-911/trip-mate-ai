# tests/utils/load_locations_csv.py

import csv
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models.location import Location


def load_locations_from_csv(csv_path: str, db: Session):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        loaded = 0
        for row in reader:
            kakao_place_id = row.get("kakao_place_id")
            if not kakao_place_id or kakao_place_id.strip() == "":
                print(f"⚠️ kakao_place_id 없음: {row.get('name')} (id: {row.get('id')})")
                continue

            loc = Location(
                id=UUID(row["id"]),
                kakao_place_id=kakao_place_id.strip(), 
                name=row["name"],
                category_group_code=row.get("category_group_code"),
                category_group_name=row.get("category_group_name"),
                category_name=row.get("category_name"),
                phone=row.get("phone"),
                address_name=row.get("address_name"),
                road_address_name=row.get("road_address_name"),
                x=float(row["x"]) if row.get("x") else 0.0,
                y=float(row["y"]) if row.get("y") else 0.0,
                place_url=row.get("place_url"),
                use_yn=row.get("use_yn", "Y"),
                delete_yn=row.get("delete_yn", "N"),
            )
            db.merge(loc)
            loaded += 1
        db.commit()
    print(f"✅ 총 {loaded}개의 장소를 DB에 로드했습니다.")
