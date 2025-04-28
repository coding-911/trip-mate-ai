from pydantic import BaseModel, EmailStr
from uuid import UUID

class SignupResponse(BaseModel):
    user_id: UUID
    token: str

class TokenResponse(BaseModel):
    token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class StatusResponse(BaseModel):
    status: str
