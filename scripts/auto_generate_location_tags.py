import random
import sys
import os
import time

# 0. 현재 파일의 상위 디렉토리 (루트)를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import uuid4

from app.db.models.location import Location
from app.db.models.location_tag import LocationTag
from app.db.models.tag import Tag
from app.db.session import SessionLocal
from app.core.config import settings

import google.generativeai as genai

# 1. Gemini 클라이언트 초기화 (환경 변수에서 API 키 불러오기)
google_api_key = settings.GOOGLE_API_KEY
if not google_api_key:
    raise Exception("GOOGLE_API_KEY 환경변수가 설정되어 있지 않습니다.")
genai.configure(api_key=google_api_key)

# 사용 가능한 모델 목록 확인
# for m in genai.list_models():
#     print(m.name, "→", m.supported_generation_methods)

model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
print("gemini 모델 생성 완료")

# 2. DB 세션 시작
db: Session = SessionLocal()

# 3. 태그가 1개 이하인 장소만 조회 (조인 기반)
subq = (
    db.query(LocationTag.location_id, func.count().label("tag_count"))
    .group_by(LocationTag.location_id)
    .subquery()
)

locations = (
    db.query(Location)
    .outerjoin(subq, Location.id == subq.c.location_id)
    .filter(
        (subq.c.tag_count <= 1) | (subq.c.tag_count == None),
        Location.use_yn == "Y",
        Location.delete_yn == "N"
    )
    .all()
)

print(f'태그가 1개 이하인 장소 수: {len(locations)}')

# 4. 각 장소에 대해 Gemini에게 태그 요청
for loc in locations:
    time.sleep(15)
    num_tags = random.randint(5, 10)
    prompt = (
        f"'{loc.name}'이라는 장소는 '{loc.category_name}' 카테고리에 속합니다. "
        f"이 장소에 어울리는 태그를 '{num_tags}'개 추천해줘. "
        "비슷한 의미의 태그는 가장 보편적이고 일반적인 단어로 골라서 의미 중복을 방지해줘."
        "태그는 모두 한국어로, 중복 없이, 붙여쓰고, 쉼표로 구분해서 출력해줘. "
        "리스트 없이 태그만 출력해줘."
    )

    print(f'Gemini에 {loc.name} 태그 요청 시작')

    try:
        response = model.generate_content(prompt)
        tag_text = response.text.strip()
        tag_names = [t.strip() for t in tag_text.split(",") if t.strip()]

        for tag_name in tag_names:
            # 태그가 이미 존재하는지 확인
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(id=uuid4(), name=tag_name)
                db.add(tag)
                db.flush()
                print(f"  ➕ 태그 생성: {tag_name}")

            # 매핑 존재 여부 확인 후 생성
            exists = db.query(LocationTag).filter_by(location_id=loc.id, tag_id=tag.id).first()
            if exists:
                print(f"  🔁 이미 매핑됨: {tag_name}")
                continue

            db.add(LocationTag(id=uuid4(), location_id=loc.id, tag_id=tag.id))
            print(f"  ✅ 매핑 추가: {tag_name}")

        db.commit()
        print(f"[{loc.name}] 태그 {len(tag_names)}개 처리 완료\n")

    except Exception as e:
        print(f"[{loc.name}] Gemini 요청 실패: {e}")
        db.rollback()

db.close()
