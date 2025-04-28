# app/db/models/user.py

import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    CHAR,
    TIMESTAMP,
    func,
    text,
    Index,
    and_
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,   
        server_default=text("uuid_generate_v4()"),
        nullable=False
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash = Column(
        "password_hash",
        String(255),
        nullable=False
    )
    name = Column(
        String(100),
        nullable=False
    )
    year_of_birth = Column(
        Integer,
        nullable=True
    )
    country_code = Column(
        String(2),
        nullable=True
    )
    use_yn = Column(
        CHAR(1),
        nullable=False,
        server_default=text("'Y'")
    )
    delete_yn = Column(
        CHAR(1),
        nullable=False,
        server_default=text("'N'")
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    __table_args__ = (
        Index(
            "ix_users_active_created_at",
            created_at,  # 문자열이 아니라 컬럼 객체를 직접
            postgresql_where=and_(
                use_yn == "Y",      # User.use_yn 대신 바로 use_yn
                delete_yn == "N"    # User.delete_yn 대신 바로 delete_yn
            )
        ),
    )