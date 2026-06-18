from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.api.core.config import get_settings
from app.api.core.exceptions import BadRequestError
from app.api.core.security import (
    generate_jti,
    hash_token,
)
from app.models.oauth_state import OAuthState
from app.helpers.auth_helper import delete_expired_oauth_records

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
OAUTH_STATE_EXPIRE_MINUTES = 10
OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES = 2


def google_start(
    db: Session,
    client_type: str,
    final_redirect_url: str,
    cookie_value: str | None = None,
) -> tuple[str, str]:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise BadRequestError("Google OAuth is not configured", code="google_oauth_not_configured")

    if client_type not in {"web", "extension"}:
        raise BadRequestError("Invalid OAuth client type", code="invalid_oauth_client")
    if client_type == "web" and not cookie_value:
        raise BadRequestError("OAuth state cookie is required", code="oauth_cookie_required")

    delete_expired_oauth_records(db)

    state = generate_jti()
    db.add(
        OAuthState(
            state_hash=hash_token(state),
            client_type=client_type,
            final_redirect_url=final_redirect_url,
            cookie_hash=hash_token(cookie_value) if cookie_value else None,
            expires_at=datetime.now(UTC) + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES),
        )
    )
    db.commit()

    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )

    return f"{GOOGLE_AUTH_URL}?{query}", state


def generate_oauth_cookie_value() -> str:
    return generate_jti()
