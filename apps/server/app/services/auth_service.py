from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from jose import JWTError, jwt
from sqlalchemy import and_, select, update
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
from app.models.refresh_token import RefreshToken
from app.models.user import User

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
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
    token_record = db.scalar(
        select(RefreshToken).where(
            and_(RefreshToken.user_id == user_id, RefreshToken.token_jti == token_jti)
        )
    )

    if token_record is None:
        raise UnauthorizedError("Refresh token not recognized")

    if token_record.revoked_at is not None:
        raise UnauthorizedError("Refresh token is revoked")

    expires_at = token_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        raise UnauthorizedError("Refresh token has expired")

    if token_record.token_hash != hash_token(refresh_token):
        raise UnauthorizedError("Refresh token mismatch")

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    new_jti = generate_jti()
    new_refresh_token, new_expires_at = create_refresh_token(user.id, new_jti)

    token_record.revoked_at = datetime.now(UTC)
    token_record.replaced_by_jti = new_jti

    db.add(
        RefreshToken(
            user_id=user.id,
            token_jti=new_jti,
            token_hash=hash_token(new_refresh_token),
            expires_at=new_expires_at,
            device_info=device_info or token_record.device_info,
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


def google_start() -> tuple[str, str]:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise BadRequestError("Google OAuth is not configured", code="google_oauth_not_configured")

    state_payload = {
        "type": "google_state",
        "nonce": generate_jti(),
        "exp": datetime.now(UTC) + timedelta(minutes=10),
    }
    state = jwt.encode(state_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

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


def _verify_google_state(state: str) -> None:
    settings = get_settings()
    try:
        payload = jwt.decode(state, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError("Invalid OAuth state") from exc

    if payload.get("type") != "google_state":
        raise UnauthorizedError("Invalid OAuth state")


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


def _complete_google_user(db: Session, code: str, state: str) -> User:
    _verify_google_state(state)
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


def google_callback(db: Session, code: str, state: str, device_info: str | None = None) -> tuple[User, str, str]:
    user = _complete_google_user(db, code, state)
    access_token, refresh_token = _issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token


def create_google_login_token(db: Session, code: str, state: str) -> str:
    user = _complete_google_user(db, code, state)
    token = generate_jti()
    db.add(
        OAuthLoginToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(minutes=OAUTH_LOGIN_TOKEN_EXPIRE_MINUTES),
        )
    )
    db.commit()
    return token


def exchange_google_login_token(
    db: Session,
    token: str,
    device_info: str | None = None,
) -> tuple[User, str, str]:
    token_record = db.scalar(select(OAuthLoginToken).where(OAuthLoginToken.token_hash == hash_token(token)))

    if token_record is None or token_record.used_at is not None:
        raise UnauthorizedError("Invalid OAuth login token")

    expires_at = token_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        raise UnauthorizedError("OAuth login token has expired")

    user = db.get(User, token_record.user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    token_record.used_at = datetime.now(UTC)
    access_token, refresh_token = _issue_token_pair(db, user, device_info=device_info)
    db.refresh(user)
    return user, access_token, refresh_token
