# TripMateAI API 명세서

## 일정(여행) 관련

### [GET] /api/v1/itinerary/user/{user_id}
- 설명: 특정 사용자의 전체 일정 및 세부 일정(step) 목록 조회
- 응답 예시:
```json
[
  {
    "itinerary": {
      "id": "uuid",
      "start_date": "2024-06-01",
      "end_date": "2024-06-03",
      ...
    },
    "steps": [
      {
        "step_id": "uuid",
        "location_id": "uuid",
        "step_order": 1,
        "date": "2024-06-01",
        ...
      }
    ]
  }
]
```

### [DELETE] /api/v1/itinerary/{itinerary_id}
- 설명: 일정 및 하위 step soft delete
- 응답: `{ "result": "success" }`

---

## 일정 Step 관련

### [POST] /api/v1/itinerary-step
- 설명: 일정 step 생성 (필요시 itinerary 자동 생성)
- 요청 예시:
```json
{
  "user_id": "uuid",
  "location_id": "uuid",
  "date": "2024-06-01",
  "start_time": "2024-06-01T09:00:00",
  "end_time": "2024-06-01T10:00:00"
}
```
- 응답: `{ "itinerary_id": "uuid", "step_id": "uuid" }`

### [PATCH] /api/v1/itinerary-step/{step_id}
- 설명: 일정 step 수정 (날짜/시간 변경 시 step_order 자동 재정렬)

### [DELETE] /api/v1/itinerary-step/{step_id}
- 설명: 일정 step soft delete (모든 step 삭제 시 itinerary도 soft delete)

---

## 추천 관련

### [GET] /api/v1/recommendations
- 설명: 사용자/위치/카테고리 기반 여행지 추천
- 파라미터: user_id, lat, lng, category 등
- 응답 예시:
```json
[
  {
    "location_id": "uuid",
    "name": "카페",
    "score": 0.92,
    ...
  }
]
```

---

## 장소 정보

### [GET] /api/v1/locations
- 설명: 장소 목록/검색/필터링

### [GET] /api/v1/locations/{location_id}
- 설명: 장소 상세 정보

---

## 북마크/이벤트/유저/인증

### [POST] /api/v1/bookmarks
### [GET] /api/v1/bookmarks
### [DELETE] /api/v1/bookmarks/{bookmark_id}

### [POST] /api/v1/user-events
### [GET] /api/v1/user-events

### [POST] /api/v1/auth/login
### [POST] /api/v1/auth/register
### [GET] /api/v1/users/me

---

> 상세 파라미터/응답 구조는 Swagger UI 및 각 스키마 참고
