from datetime import datetime
import uuid
from sqlalchemy import Boolean, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    is_email_verified: Mapped[bool] = mapped_column(default=False)
    email_verified_at: Mapped[datetime | None]

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    items = relationship("SavedItem", back_populates="user", cascade="all, delete-orphan")
    email_verification_token = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
