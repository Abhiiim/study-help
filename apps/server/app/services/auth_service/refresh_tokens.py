from datetime import UTC, datetime

from sqlalchemy import and_, update
from sqlalchemy.orm import Session

from app.api.core.exceptions import UnauthorizedError
from app.api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_jti,
    hash_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


def refresh_tokens(db: Session, refresh_token: str, device_info: str | None = None) -> tuple[User, str, str]:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")

    user_id_raw = payload.get("sub")
    token_jti = payload.get("jti")
    if not user_id_raw or not token_jti:
        raise UnauthorizedError("Invalid refresh token")

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid refresh token") from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    new_jti = generate_jti()
    new_refresh_token, new_expires_at = create_refresh_token(user.id, new_jti)
    now = datetime.now(UTC)

    rotated = db.execute(
        update(RefreshToken)
        .where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.token_jti == token_jti,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.token_hash == hash_token(refresh_token),
                RefreshToken.expires_at > now,
            )
        )
        .values(revoked_at=now, replaced_by_jti=new_jti)
    )

    if rotated.rowcount != 1:
        db.rollback()
        raise UnauthorizedError("Refresh token is invalid, expired, or already used")

    db.add(
        RefreshToken(
            user_id=user.id,
            token_jti=new_jti,
            token_hash=hash_token(new_refresh_token),
            expires_at=new_expires_at,
            device_info=device_info,
        )
    )

    access_token = create_access_token(user.id)
    db.commit()
    return user, access_token, new_refresh_token
