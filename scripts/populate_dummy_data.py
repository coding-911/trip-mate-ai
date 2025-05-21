import random
import sys
import os

# 현재 파일의 상위 디렉토리 (루트)를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.location import Location
from app.db.models.bookmark import Bookmark
from app.core.config import settings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from uuid import uuid4
from datetime import datetime, timedelta

db: Session = SessionLocal()

# 1. 장소 불러오기
locations = db.query(Location).filter(
    Location.use_yn == "Y",
    Location.delete_yn == "N"
).all()

if not locations:
    raise Exception("장소가 없습니다.")

# 2. 사용자 생성 (300명)
users = []
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

for i in range(300):
    u = User(
        id=uuid4(),
        email=f"user{i}@test.com",
        password_hash=pwd_context.hash("1234"),
        name=f"User{i}",
        year_of_birth=random.randint(1950, 2010),
        country_code="KR",
        use_yn="Y",
        delete_yn="N"
    )
    db.add(u)
    users.append(u)

db.commit()

# 3. 북마크 생성 (유저당 5~10개)
for user in users:
    bookmarked = random.sample(locations, random.randint(5, 10))
    for loc in bookmarked:
        db.add(Bookmark(user_id=user.id, location_id=loc.id))

db.commit()

# 4. Elasticsearch 로그 생성 (view, click, bookmark만)
es = Elasticsearch([settings.ELASTICSEARCH_HOSTS])
actions = ["view", "click", "bookmark"]
logs = []

for user in users:
    num_logs = random.randint(50, 100)  # 사용자당 행동 로그 50~100건
    for _ in range(num_logs):
        loc = random.choice(locations)
        action = random.choices(actions, weights=[0.6, 0.3, 0.1])[0]  # actions 가중치 부여
        days_ago = random.randint(0, 30)
        seconds_offset = random.randint(0, 86400)
        timestamp = datetime.now() - timedelta(days=days_ago, seconds=seconds_offset)

        logs.append({
            "_index": "user-logs",
            "_source": {
                "user_id": str(user.id),
                "location_id": str(loc.id),
                "action": action,
                "timestamp": timestamp.isoformat()
            }
        })

# Bulk insert into Elasticsearch
bulk(es, logs)

print("딥러닝을 위한 더미 데이터 대량 생성 완료")
