from datetime import UTC, datetime, timedelta
from sqlalchemy.orm import Session

from app.api.core.security import (
    generate_jti,
    hash_token,
)
from app.models.auth_token import AuthToken
from app.models.user import User
from app.helpers.auth_helper import complete_google_user, consume_google_state, delete_expired_oauth_records, issue_token_pair
from app.enums.auth_token import TokenType

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
OAUTH_STATE_EXPIRE_MINUTES = 10
OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES = 2


def google_callback(
    db: Session,
    code: str,
    state: str,
    device_info: str | None = None,
    cookie_value: str | None = None,
) -> tuple[User, str, str]:
    consume_google_state(db, state, cookie_value=cookie_value)
    user = complete_google_user(db, code)
    access_token, refresh_token = issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token


def create_google_login_token(
    db: Session,
    code: str,
    state: str,
    cookie_value: str | None = None,
) -> tuple[str, str, str]:
    client_type, final_redirect_url = consume_google_state(db, state, cookie_value=cookie_value)
    user = complete_google_user(db, code)
    delete_expired_oauth_records(db)
    token = generate_jti()
    db.add(
        AuthToken(
            user_id=user.id,
            type=TokenType.OAUTH_LOGIN,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(minutes=OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES),
        )
    )
    db.commit()
    return token, final_redirect_url, client_type
