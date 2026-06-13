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
from app.models.oauth_login_token import OAuthLoginToken
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


def _issue_token_pair(db: Session, user: User, device_info: str | None = None) -> tuple[str, str]:
    access_token = create_access_token(user.id)

    new_jti = generate_jti()
    refresh_token, refresh_expires_at = create_refresh_token(user.id, new_jti)

    db.add(
        RefreshToken(
            user_id=user.id,
            token_jti=new_jti,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires_at,
            device_info=device_info,
        )
    )
    db.commit()

    return access_token, refresh_token


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _delete_expired_oauth_records(db: Session) -> None:
    now = datetime.now(UTC)
    db.execute(delete(OAuthState).where(OAuthState.expires_at <= now))
    db.execute(delete(OAuthLoginToken).where(OAuthLoginToken.expires_at <= now))


def signup(db: Session, email: str, password: str, device_info: str | None = None) -> tuple[User, str, str]:
    email = normalize_email(email)
    ensure_gmail(email)

    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ConflictError("Email is already registered", code="email_exists")

    user = User(email=email, password_hash=hash_password(password), is_active=True)
    db.add(user)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Email is already registered", code="email_exists") from exc

    access_token, refresh_token = _issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token


def login(db: Session, email: str, password: str, device_info: str | None = None) -> tuple[User, str, str]:
    email = normalize_email(email)
    ensure_gmail(email)

    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        raise UnauthorizedError("Invalid email or password")

    if not user.password_hash:
        raise UnauthorizedError("Use Google sign-in for this account")

    if not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    access_token, refresh_token = _issue_token_pair(db, user, device_info=device_info)
    return user, access_token, refresh_token


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


def generate_oauth_cookie_value() -> str:
    return generate_jti()


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

    _delete_expired_oauth_records(db)

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


def _consume_google_state(db: Session, state: str, cookie_value: str | None = None) -> tuple[str, str]:
    state_record = db.scalar(select(OAuthState).where(OAuthState.state_hash == hash_token(state)))
    now = datetime.now(UTC)

    if state_record is None:
        raise UnauthorizedError("Invalid OAuth state")
    if state_record.used_at is not None:
        raise UnauthorizedError("OAuth state was already used")
    if _as_aware_utc(state_record.expires_at) <= now:
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


def _exchange_google_code(code: str) -> dict:
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


def _complete_google_user(db: Session, code: str) -> User:
    profile = _exchange_google_code(code)

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

    if user is None:
        user = User(email=email, password_hash=None, google_sub=sub, is_active=True)
        db.add(user)
        try:
            db.flush()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError("A user with this email already exists", code="email_exists") from exc
    elif user.google_sub is None:
        user.google_sub = sub

    db.commit()
    db.refresh(user)
    return user


def google_callback(
    db: Session,
    code: str,
    state: str,
    device_info: str | None = None,
    cookie_value: str | None = None,
) -> tuple[User, str, str]:
    _consume_google_state(db, state, cookie_value=cookie_value)
    user = _complete_google_user(db, code)
    access_token, refresh_token = _issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token


def create_google_login_token(
    db: Session,
    code: str,
    state: str,
    cookie_value: str | None = None,
) -> tuple[str, str, str]:
    client_type, final_redirect_url = _consume_google_state(db, state, cookie_value=cookie_value)
    user = _complete_google_user(db, code)
    _delete_expired_oauth_records(db)
    token = generate_jti()
    db.add(
        OAuthLoginToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(minutes=OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES),
        )
    )
    db.commit()
    return token, final_redirect_url, client_type


def exchange_google_login_token(
    db: Session,
    token: str,
    device_info: str | None = None,
) -> tuple[User, str, str]:
    token_record = db.scalar(select(OAuthLoginToken).where(OAuthLoginToken.token_hash == hash_token(token)))
    now = datetime.now(UTC)

    if token_record is None or token_record.used_at is not None:
        raise UnauthorizedError("Invalid OAuth login token")

    if _as_aware_utc(token_record.expires_at) <= now:
        raise UnauthorizedError("OAuth login token has expired")

    consumed = db.execute(
        update(OAuthLoginToken)
        .where(and_(OAuthLoginToken.id == token_record.id, OAuthLoginToken.used_at.is_(None)))
        .values(used_at=now)
    )
    if consumed.rowcount != 1:
        db.rollback()
        raise UnauthorizedError("Invalid OAuth login token")

    user = db.get(User, token_record.user_id)
    if user is None or not user.is_active:
        db.rollback()
        raise UnauthorizedError("User not found or inactive")

    access_token, refresh_token = _issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token
