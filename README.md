# TripMateAI

AI 기반의 스마트한 여행 추천 및 계획 서비스

## 목차
- [소개](#소개)
- [핵심 기능](#핵심-기능)
- [추천 시스템](#추천-시스템)
- [기술 스택](#기술-스택)
- [시작하기](#시작하기)
- [API 문서](#api-문서)
- [개발 가이드](#개발-가이드)
- [라이선스](#라이선스)

## 소개

TripMateAI는 사용자 맞춤형 여행지 추천과 일정 관리를 제공하는 서비스입니다. FastAPI 기반의 백엔드 시스템과 하이브리드 추천 알고리즘을 통해 효율적이고 개인화된 여행 경험을 제공합니다.

## 핵심 기능

- 🎯 **AI 기반 맞춤형 추천**
  - 사용자의 취향과 행동 패턴 기반 여행지 추천
  - 위치 기반 실시간 주변 명소 추천
  - 카테고리 기반 다양성 있는 추천

- 👤 **사용자 경험**
  - 직관적인 인증 및 프로필 관리 (`/api/v1/auth`, `/api/v1/users`)
  - 개인화된 북마크 기능 (`/api/v1/bookmarks`)
  - 사용자 활동 기반 피드백 시스템 (`/api/v1/user-events`)

- 📍 **여행지 정보**
  - 카카오 Places API 연동 실시간 정보
  - 상세한 장소 정보 및 카테고리 관리 (`/api/v1/locations`)
  - 위치 기반 검색 및 필터링

## 추천 시스템

TripMateAI의 추천 시스템은 협업 필터링과 콘텐츠 기반 필터링을 결합한 하이브리드 방식을 사용합니다.

### 데이터 수집 및 전처리

1. **사용자 행동 데이터**
   - Elasticsearch 기반 행동 로그 수집
   - 행동 유형별 가중치 차등 적용:
     - 조회(view): 1.0
     - 클릭(click): 2.0
     - 북마크(bookmark): 3.0

2. **여행지 특징 데이터**
   - 카카오 Places API 연동
   - 계층형 카테고리 태그 추출
   - MultiLabelBinarizer 기반 특징 벡터화

### 모델 아키텍처

- **프레임워크**: LightFM (Hybrid Matrix Factorization)
- **주요 파라미터**:
  - Loss function: WARP (Weighted Approximate-Rank Pairwise)
  - Embedding dimension: 64
  - Learning rate: 0.03
  - Epochs: 50

### 성능 평가

- **정확도 지표**
  - Precision@5: 상위 5개 추천의 정확도
  - Recall@k: 상위 k개(5/10/20) 추천의 재현율
  - AUC: ROC 곡선 아래 면적

### 운영 프로세스

1. **일괄 처리**
   - 일간 모델 재학습
   - 버전 관리 및 모델 백업

2. **실시간 서빙**
   - Redis 기반 추천 결과 캐싱
   - 거리 기반 동적 필터링
   - 카테고리 다양성 보장

## 기술 스택

### 백엔드
- **Framework**: FastAPI 0.115.12
- **Database**: PostgreSQL (psycopg2-binary 2.9.10)
- **ORM**: SQLAlchemy 2.0.40
- **Migration**: Alembic
- **API Documentation**: OpenAPI (Swagger UI)

### 검색 엔진 & 캐싱
- **Search Engine**: Elasticsearch 8.x
- **Cache**: Redis 5.x

### 개발 도구
- **Testing**: pytest
- **Container**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 프로젝트 구조

```
TripMateAI/
├── app/                    # 메인 애플리케이션
│   ├── api/               # API 엔드포인트
│   ├── core/              # 핵심 설정
│   ├── db/                # 데이터베이스 관련
│   ├── services/          # 비즈니스 로직
│   └── ai_engine/         # AI 추천 엔진
├── alembic/               # DB 마이그레이션
├── tests/                 #테스트 코드
└── scripts/               # 유틸리티 스크립트
```

## 시작하기

### 필수 요구사항

- Python 3.8 이상
- PostgreSQL
- Docker & Docker Compose
- Redis
- Elasticsearch

### 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/coding-911/trip-mate-ai.git
cd TripMateAI
```

2. 가상환경 생성 및 의존성 설치
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일에서 필요한 설정을 수정하세요
```

4. Docker 컨테이너 실행
```bash
docker-compose up -d
```

5. 데이터베이스 마이그레이션
```bash
alembic upgrade head
```

6. 개발 서버 실행
```bash
uvicorn app.main:app --reload
```

## API 문서

### Swagger UI
- URL: `http://localhost:8000/docs`
- 모든 API 엔드포인트의 상세 명세
- 실시간 API 테스트 가능

### 주요 API 엔드포인트
- `/api/v1/auth`: 인증 관련 API
- `/api/v1/users`: 사용자 관리 API
- `/api/v1/locations`: 여행지 정보 API
- `/api/v1/recommendations`: 추천 시스템 API
- `/api/v1/bookmarks`: 북마크 관리 API
- `/api/v1/user-events`: 사용자 활동 로깅 API

## 개발 가이드

### 테스트 실행
```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/api/
pytest tests/services/

# 커버리지 리포트 생성
pytest --cov=app tests/
```

### 코드 품질 관리
- pre-commit hooks 설정
- GitHub Actions를 통한 CI/CD
- 코드 리뷰 가이드라인 준수

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

