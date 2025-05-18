from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.location import Location
from app.db.models.bookmark import UserBookmark
from app.core.config import settings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from uuid import uuid4
import random
from datetime import datetime, timedelta

db: Session = SessionLocal()

# 1. 장소 불러오기
locations = db.query(Location).filter(
    Location.use_yn == "Y",
    Location.delete_yn == "N"
).all()

if not locations:
    raise Exception("장소가 없습니다.")

# 2. 사용자 1000명 생성
users = []
for i in range(1000):
    u = User(
        id=uuid4(),
        email=f"user{i}@test.com",
        password_hash="dummyhash",
        name=f"User{i}",
        year_of_birth=random.randint(1970, 2010),
        country_code="KR",
        use_yn="Y",
        delete_yn="N"
    )
    db.add(u)
    users.append(u)

db.commit()

# 3. 북마크 (유저당 5~10개)
for user in users:
    bookmarked = random.sample(locations, random.randint(5, 10))
    for loc in bookmarked:
        db.add(UserBookmark(user_id=user.id, location_id=loc.id))

db.commit()

# 4. 유저 이벤트 로그 (Elasticsearch)
es = Elasticsearch([settings.ELASTICSEARCH_HOSTS])
actions = ["view", "click", "bookmark"]
logs = []

for user in users:
    num_logs = random.randint(200, 500)
    for _ in range(num_logs):
        loc = random.choice(locations)
        action = random.choice(actions)
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
