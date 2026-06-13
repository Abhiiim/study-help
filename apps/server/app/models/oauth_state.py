from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class OAuthState(Base, TimestampMixin):
    __tablename__ = "oauth_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    state_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    client_type: Mapped[str] = mapped_column(String(20), nullable=False)
    final_redirect_url: Mapped[str] = mapped_column(Text, nullable=False)
    cookie_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
