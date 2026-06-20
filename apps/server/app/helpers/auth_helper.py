from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.core.config import get_settings
from app.api.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_jti,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.auth_token import AuthToken
from app.models.oauth_state import OAuthState
from app.models.refresh_token import RefreshToken
from app.models.user import User

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
OAUTH_STATE_EXPIRE_MINUTES = 10
OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES = 2


def normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_gmail(email: str) -> None:
    if not normalize_email(email).endswith("@gmail.com"):
        raise BadRequestError("Only @gmail.com accounts are allowed", code="gmail_only")


def issue_token_pair(db: Session, user: User, device_info: str | None = None) -> tuple[str, str]:
    access_token = create_access_token(user.id)

    new_jti = generate_jti()
    refresh_token, refresh_expires_at = create_refresh_token(user.id, new_jti)

    db.add(
        RefreshToken(
            user_id = user.id,
            token_jti = new_jti,
            token_hash = hash_token(refresh_token),
            expires_at = refresh_expires_at,
            device_info = device_info,
        )
    )
    db.commit()

    return access_token, refresh_token


def as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def delete_expired_oauth_records(db: Session) -> None:
    now = datetime.now(UTC)
    db.execute(delete(OAuthState).where(OAuthState.expires_at <= now))
    db.execute(delete(AuthToken).where(AuthToken.expires_at <= now))


def consume_google_state(db: Session, state: str, cookie_value: str | None = None) -> tuple[str, str]:
    state_record = db.scalar(select(OAuthState).where(OAuthState.state_hash == hash_token(state)))
    now = datetime.now(UTC)

    if state_record is None:
        raise UnauthorizedError("Invalid OAuth state")
    if state_record.used_at is not None:
        raise UnauthorizedError("OAuth state was already used")
    if as_aware_utc(state_record.expires_at) <= now:
        raise UnauthorizedError("OAuth state has expired")
    if state_record.client_type == "web":
        if not cookie_value or state_record.cookie_hash != hash_token(cookie_value):
            raise UnauthorizedError("OAuth state cookie mismatch")

    consumed = db.execute(
        update(OAuthState)
        .where(and_(OAuthState.id == state_record.id, OAuthState.used_at.is_(None)))
        .values(used_at=now)
    )
    if consumed.rowcount != 1:
        db.rollback()
        raise UnauthorizedError("OAuth state was already used")

    db.commit()
    return state_record.client_type, state_record.final_redirect_url


def exchange_google_code(code: str) -> dict:
    settings = get_settings()
    try:
        with httpx.Client(timeout=10.0) as client:
            token_response = client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            tokens = token_response.json()

            access_token = tokens.get("access_token")
            if not access_token:
                raise UnauthorizedError("Google access token missing")

            userinfo_response = client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            userinfo_response.raise_for_status()
            return userinfo_response.json()
    except httpx.HTTPError as exc:
        raise UnauthorizedError("Google OAuth exchange failed") from exc


def complete_google_user(db: Session, code: str) -> User:
    profile = exchange_google_code(code)

    email = normalize_email(profile.get("email", ""))
    sub = profile.get("sub")
    email_verified = bool(profile.get("email_verified"))

    if not sub or not email:
        raise UnauthorizedError("Google profile is missing required fields")
    if not email_verified:
        raise UnauthorizedError("Google email must be verified")
    ensure_gmail(email)

    user = db.scalar(select(User).where(User.google_sub == sub))
    if user is None:
        user = db.scalar(select(User).where(User.email == email))

    now = datetime.now(UTC)
    if user is not None and not user.is_active:
        raise UnauthorizedError("Account is disabled")

    if user is None:
        user = User(
            email=email,
            password_hash=None,
            google_sub=sub,
            is_active=True,
            is_email_verified=True,
            email_verified_at=now,
        )
        db.add(user)
        try:
            db.flush()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError("A user with this email already exists", code="email_exists") from exc
    elif user.google_sub is None:
        user.google_sub = sub

    if not user.is_email_verified:
        user.is_email_verified = True
        user.email_verified_at = now

    db.commit()
    db.refresh(user)
    return user
