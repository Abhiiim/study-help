from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.core.exceptions import UnauthorizedError
from app.api.core.security import (
    verify_password,
)
from app.models.user import User
from app.helpers.auth_helper import ensure_gmail, issue_token_pair, normalize_email


def login(db: Session, email: str, password: str, device_info: str | None = None) -> tuple[User, str, str]:
    user = _authenticate(db, email, password)

    access_token, refresh_token = issue_token_pair(db, user, device_info=device_info)
    
    return user, access_token, refresh_token


def _authenticate(db: Session, email: str, password: str) -> User:
    email = normalize_email(email)
    ensure_gmail(email)

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise UnauthorizedError(
            "Invalid email or password",
            code="invalid_credentials",
        )

    # TODO: Need to add account linking later on.
    if not user.password_hash:
        raise UnauthorizedError("Use Google sign-in for this account")

    if not user.is_active:
        raise UnauthorizedError(
            "Account is disabled",
            code="account_disabled",
        )

    if not user.is_email_verified:
        raise UnauthorizedError(
            "Please verify your email first",
            code="email_not_verified",
        )

    if not verify_password(password, user.password_hash):
        raise UnauthorizedError(
            "Invalid email or password",
            code="invalid_credentials",
        )

    return user
