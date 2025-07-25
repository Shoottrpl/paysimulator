from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class RefreshToken(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(512), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @hybrid_property
    def is_active(self) -> bool:
        return self.expires_at > datetime.now(timezone.utc)

    @is_active.expression
    def is_active(cls):
        return cls.expires_at > func.now()


class RevokedToken(Base):
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_type: Mapped[str] = mapped_column(String(10), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at = None
    updated_at = None

    @hybrid_property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now(timezone.utc)

    @is_expired.expression
    def is_expired(cls):
        return cls.expires_at < func.now()
