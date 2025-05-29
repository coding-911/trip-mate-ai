
# TripMateAI

AI 기반의 스마트 여행 추천 및 일정 관리 서비스

---

## 목차
- [소개](#소개)
- [주요 기능](#주요-기능)
- [추천 시스템](#추천-시스템)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [시작하기](#시작하기)
- [API 문서](#api-문서)
- [API 명세서(전체)](docs/api_spec.md)
- [개발 가이드](#개발-가이드)
- [라이선스](#라이선스)

---

## 소개

- TripMateAI는 사용자의 취향, 행동 로그, 장소 태그 등 다양한 정보를 활용해 맞춤형 여행지 추천과 일정 관리를 제공하는 AI 기반 여행 플랫폼입니다.  
- FastAPI 기반의 RESTful 백엔드, 하이브리드 추천 시스템, 서비스 계층 분리 등 실서비스 수준의 설계와 테스트를 갖추고 있습니다.

---

## 주요 기능

- **AI 맞춤 여행지 추천**
  - 행동 로그 및 장소 태그 기반 하이브리드 추천 (LightFM)
  - 실시간/카테고리/거리 기반 추천
- **여행 일정/세부 일정(스텝) 관리**
  - 일정/스텝 CRUD, step_order 자동 정렬, soft delete 지원
  - 사용자별 전체 일정/스텝 일괄 조회 및 삭제
- **장소 정보/검색**
  - 카카오 Places API 연동, 상세 정보 제공
  - 위치 기반 검색, 카테고리 필터링
- **사용자/인증/북마크/이벤트**
  - JWT 인증, 프로필 관리, 북마크, 사용자 행동 이벤트 기록

---

## 추천 시스템

- **모델**: LightFM 기반 하이브리드 추천 (행동 로그 + 장소 태그)
- **행동 로그**: 조회/클릭/북마크 등 이벤트별 가중치 부여, Elasticsearch 저장
- **장소 태그**: 카카오 API 기반 멀티라벨 벡터화
- **지표**: Precision@5, Recall@k, AUC 등
- **운영**: 일간 재학습, Redis 캐싱, 거리/카테고리 다양성 보장

---

## 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, Alembic, Pydantic
- **DB**: PostgreSQL
- **검색/캐시**: Elasticsearch, Redis
- **AI/추천**: LightFM, Scipy
- **테스트**: pytest, testcontainers
- **배포/운영**: Docker, Docker Compose, GitHub Actions

> 주요 패키지:  
> fastapi, sqlalchemy, psycopg2-binary, elasticsearch, redis, lightfm, scipy, pydantic, pytest 등  
> (자세한 버전은 requirements.txt 참고)

---

## 프로젝트 구조

```
TripMateAI/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routers/         # RESTful 라우터 (itinerary, itinerary_step, recommendations 등)
│   │       └── schemas/         # Pydantic 스키마 (일정, 스텝, 장소, 유저 등)
│   ├── services/                # 비즈니스 로직 (itinerary_service 등)
│   ├── db/                      # DB 모델, 세션, 마이그레이션
│   ├── ai_engine/               # 추천 엔진 및 피처 처리
│   ├── core/                    # 설정, 유틸
│   └── main.py                  # FastAPI 엔트리포인트
├── tests/                       # 통합/단위 테스트
├── scripts/                     # 데이터 적재/유틸 스크립트
├── alembic/                     # DB 마이그레이션
├── requirements.txt             # Python 패키지 목록
├── docker-compose.yaml          # 서비스 오케스트레이션
└── README.md
```

---

## 시작하기

### 요구사항
- Python 3.8+
- PostgreSQL
- Redis
- Elasticsearch
- Docker, Docker Compose

### 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/coding-911/trip-mate-ai.git
cd TripMateAI

# 2. 가상환경 및 의존성 설치
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 4. Docker 서비스 실행
docker-compose up -d

# 5. DB 마이그레이션
alembic upgrade head

# 6. 개발 서버 실행
uvicorn app.main:app --reload
```

---

## API 문서

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API 명세서(전체)**: [docs/api_spec.md](docs/api_spec.md)
- **주요 엔드포인트**
  - `/api/v1/itinerary` : 일정 전체 조회/삭제
  - `/api/v1/itinerary-step` : 일정 스텝 CRUD
  - `/api/v1/recommendations` : 추천 API
  - `/api/v1/locations` : 장소 정보/검색
  - `/api/v1/bookmarks` : 북마크
  - `/api/v1/user-events` : 사용자 이벤트
  - `/api/v1/auth`, `/api/v1/users` : 인증/유저 관리

---

## 개발 가이드

- **테스트 실행**
  ```bash
  pytest
  ```
- **코드 품질**
  - pre-commit, GitHub Actions, 코드리뷰 가이드 적용

---

## 라이선스

MIT License  
자세한 내용은 [LICENSE](LICENSE) 참고

---

**문의/기여 환영!**

---

필요시 예시/샘플 요청, 상세 API 명세, ERD 등도 추가 가능합니다.  
(실제 서비스 구조와 기술스택, 기능을 모두 반영한 최신 README입니다.)
