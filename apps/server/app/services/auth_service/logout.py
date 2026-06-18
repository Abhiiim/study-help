from datetime import UTC, datetime

from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session

from app.api.core.exceptions import BadRequestError, UnauthorizedError
from app.api.core.security import decode_token
from app.models.refresh_token import RefreshToken
from app.models.user import User


def logout(db: Session, user: User, refresh_token: str | None, logout_all: bool) -> None:
    now = datetime.now(UTC)

    if logout_all:
        db.execute(
            update(RefreshToken)
            .where(and_(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)))
            .values(revoked_at=now)
        )
        db.commit()
        return

    if not refresh_token:
        raise BadRequestError("refresh_token is required unless logout_all=true")

    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")

    token_jti = payload.get("jti")
    user_id_raw = payload.get("sub")
    try:
        user_id = int(user_id_raw) if user_id_raw else None
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid refresh token") from exc

    if not token_jti or user_id != user.id:
        raise UnauthorizedError("Invalid refresh token")

    token_record = db.scalar(
        select(RefreshToken).where(
            and_(RefreshToken.user_id == user.id, RefreshToken.token_jti == token_jti)
        )
    )
    if token_record is None:
        raise UnauthorizedError("Refresh token not recognized")

    token_record.revoked_at = now
    db.commit()


def logout_by_refresh_token(db: Session, refresh_token: str, logout_all: bool = False) -> None:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")

    user_id_raw = payload.get("sub")
    token_jti = payload.get("jti")
    try:
        user_id = int(user_id_raw) if user_id_raw else None
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid refresh token") from exc

    if not user_id or not token_jti:
        raise UnauthorizedError("Invalid refresh token")

    now = datetime.now(UTC)
    if logout_all:
        db.execute(
            update(RefreshToken)
            .where(and_(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)))
            .values(revoked_at=now)
        )
        db.commit()
        return

    revoked = db.execute(
        update(RefreshToken)
        .where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.token_jti == token_jti,
                RefreshToken.revoked_at.is_(None),
            )
        )
        .values(revoked_at=now)
    )

    if revoked.rowcount != 1:
        db.rollback()
        raise UnauthorizedError("Refresh token not recognized")

    db.commit()
