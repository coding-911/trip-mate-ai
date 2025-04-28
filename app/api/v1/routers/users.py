# app/api/v1/routers/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.services.user_service import (
    create_user,
    get_user,
    get_user_by_email,   # ← 여기서 직접 import
    list_users,
    delete_user
)
from app.core.security import get_password_hash, create_access_token
from app.api.v1.schemas import (
    UserCreate,
    UserRead,
    SignupResponse,
    StatusResponse
)

router = APIRouter(prefix="/user", tags=["user"])

@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    # 서비스 계층 함수를 직접 호출해서 중복 검사
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 비밀번호 해싱
    hashed = get_password_hash(user_in.password)

    # 사용자 생성
    user = create_user(
        db,
        email=user_in.email,
        name=user_in.name,
        password_hash=hashed,
        year_of_birth=user_in.year_of_birth,
        country_code=user_in.country_code
    )

    # JWT 토큰 발행
    token = create_access_token({"sub": str(user.id)})

    return SignupResponse(user_id=user.id, token=token)

@router.get("/", response_model=List[UserRead])
def read_users(db: Session = Depends(get_db)):
    return list_users(db)

@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/{user_id}", response_model=StatusResponse)
def remove_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return StatusResponse(status="deleted")
