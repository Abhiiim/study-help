from datetime import UTC, datetime
from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session

from app.api.core.exceptions import UnauthorizedError
from app.api.core.security import (
    hash_token,
)
from app.models.auth_token import AuthToken
from app.models.user import User
from app.helpers.auth_helper import as_aware_utc, issue_token_pair
from app.enums.auth_token import TokenType

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
OAUTH_STATE_EXPIRE_MINUTES = 10
OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES = 2


def exchange_google_login_token(
    db: Session,
    token: str,
    device_info: str | None = None,
) -> tuple[User, str, str]:
    token_record = db.scalar(
        select(AuthToken)
        .where(and_(
            AuthToken.token_hash == hash_token(token),
            AuthToken.type == TokenType.OAUTH_LOGIN
        ))
    )
    now = datetime.now(UTC)

    if token_record is None or token_record.used_at is not None:
        raise UnauthorizedError("Invalid OAuth login token")

    if as_aware_utc(token_record.expires_at) <= now:
        raise UnauthorizedError("OAuth login token has expired")

    consumed = db.execute(
        update(AuthToken)
        .where(and_(
            AuthToken.id == token_record.id, 
            AuthToken.type == TokenType.OAUTH_LOGIN,
            AuthToken.used_at.is_(None)
        ))
        .values(used_at=now)
    )
    if consumed.rowcount != 1:
        db.rollback()
        raise UnauthorizedError("Invalid OAuth login token")

    user = db.get(User, token_record.user_id)
    if user is None or not user.is_active:
        db.rollback()
        raise UnauthorizedError("User not found or inactive")

    access_token, refresh_token = issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token
