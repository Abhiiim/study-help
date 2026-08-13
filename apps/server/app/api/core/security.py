import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.api.core.config import get_settings
from app.api.core.exceptions import UnauthorizedError

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, password_hash_value: str) -> bool:
    return password_hash.verify(password, password_hash_value)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_jti() -> str:
    return secrets.token_urlsafe(24)


def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    settings = get_settings()
    to_encode = payload.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    return _create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int, jti: str) -> tuple[str, datetime]:
    settings = get_settings()
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expires_at = datetime.now(UTC) + expires_delta
    token = _create_token(
        {"sub": str(user_id), "type": "refresh", "jti": jti},
        expires_delta,
    )
    return token, expires_at


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
