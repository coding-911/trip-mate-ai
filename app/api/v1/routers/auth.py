from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.user_service import get_user_by_email
from app.core.security import verify_password, create_access_token
from app.api.v1.schemas import LoginRequest, TokenResponse, StatusResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(token=token)

@router.post("/logout", response_model=StatusResponse)
def logout():
    # JWT 세션 관리 로직이 없다면 단순 메시지 반환
    return StatusResponse(status="logged out")
