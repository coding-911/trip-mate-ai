from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. SQLAlchemy 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# 2. 세션팩토리 설정
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. FastAPI 의존성으로 쓸 get_db 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
