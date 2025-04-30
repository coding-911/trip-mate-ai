import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient


from app.db.base import Base
from app.db.session import get_db
from app.main import app

# In-memory SQLite URL for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine and session
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 모든 세션이 같은 메모리 DB를 쓰도록
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(autouse=True)
def clear_tables(db_session):
    # Ensure isolation: clear tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

@pytest.fixture(scope="session", autouse=True)
def prepare_db():
    # Create schema before tests and drop after
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    # Provide a new database session for a test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(db_session):
    # Override FastAPI's get_db to use test session
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
