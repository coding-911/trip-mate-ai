# tests/conftest.py
import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from elasticsearch import Elasticsearch
from testcontainers.elasticsearch import ElasticSearchContainer

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.services import user_event_service
from app.core.config import settings

# ─── in-memory SQLite 설정 ────────────────────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_db():
    """
    테스트 전체 시작 전에 스키마 생성, 끝나면 drop.
    """
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(autouse=True)
def clear_tables(db_session):
    """
    각 테스트가 독립적으로 실행되도록,
    테스트 전후로 모든 테이블을 비웁니다.
    """
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture()
def db_session():
    """
    테스트 하나당 새로운 DB 세션 제공.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── FastAPI TestClient (DB 전용) ─────────────────────────────────────────────
@pytest.fixture()
def client(db_session) -> TestClient:
    """
    get_db 의존성을 테스트용 세션으로 오버라이드한 TestClient.
    ES 없이도 돌릴 수 있는 "DB 전용" 클라이언트.
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ─── Elasticsearch Container 설정 ────────────────────────────────────────────
@pytest.fixture(scope="session")
def es_container():
    """
    테스트 전체에 하나 띄우는 ElasticSearchContainer.
    settings.ELASTICSEARCH_HOSTS 를 컨테이너 URL로 덮어씁니다.
    """
    with ElasticSearchContainer("docker.elastic.co/elasticsearch/elasticsearch:8.15.2") as ctr:
        url = ctr.get_url()
        settings.ELASTICSEARCH_HOSTS = [url]
        # 컨테이너 기동 대기
        time.sleep(5)
        yield ctr
        # 컨테이너 자동 정리됨


# ─── ES 통합 테스트용 TestClient ──────────────────────────────────────────────
@pytest.fixture()
def es_test_client(es_container, client) -> TestClient:
    host = es_container.get_container_host_ip()
    port = es_container.get_exposed_port(9200)
    url = f"http://{host}:{port}"

    # ✅ Elasticsearch 인스턴스를 새로 만들어 app에 주입
    new_es = Elasticsearch([url])
    user_event_service.es = new_es

    # ✅ 인덱스 존재 확인 및 생성
    for _ in range(60):
        try:
            if new_es.ping():
                break
        except Exception:
            time.sleep(0.5)
    else:
        raise RuntimeError("Elasticsearch did not start in time.")

    if not new_es.indices.exists(index="user-events"):
        new_es.indices.create(
            index="user-events",
            body={
                "mappings": {
                    "properties": {
                        "user_id":     {"type": "keyword"},
                        "location_id": {"type": "keyword"},
                        "action":      {"type": "keyword"},
                        "timestamp":   {"type": "date"},
                    }
                }
            }
        )

    return client

