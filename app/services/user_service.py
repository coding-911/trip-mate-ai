from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models.user import User

def create_user(db: Session, email: str, name: str, password_hash: str,
                year_of_birth: Optional[int], country_code: Optional[str]) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
        year_of_birth=year_of_birth,
        country_code=country_code
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User)\
        .filter(User.id == user_id, User.use_yn=="Y", User.delete_yn=="N")\
        .first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User)\
        .filter(User.email == email, User.use_yn=="Y", User.delete_yn=="N")\
        .first()

def list_users(db: Session) -> List[User]:
    return db.query(User)\
        .filter(User.use_yn=="Y", User.delete_yn=="N")\
        .all()

def delete_user(db: Session, user_id: UUID) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    user.delete_yn = "Y"
    db.commit()
    return True
