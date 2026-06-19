from datetime import UTC, datetime, timedelta
import secrets

from sqlalchemy import and_, delete, select, update
from sqlalchemy.orm import Session

from app.models import AuthToken, RefreshToken, User
from app.api.core.security import hash_password, hash_token
from app.enums.auth_token import TokenType
from app.api.core.exceptions import UnauthorizedError
from app.helpers.auth_helper import as_aware_utc, normalize_email
from app.api.core.config import get_settings
from app.services.notification_service.email_service import send_email

PASSWORD_RESET_EXPIRY_MINUTES = 15


def forgot_password(
    db: Session,
    email: str,
) -> str | None:
    email = normalize_email(email)

    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Don't reveal whether user exists
    if user is None:
        return None

    now = datetime.now(UTC)

    # Invalidate previous unused reset tokens
    db.execute(
        update(AuthToken)
        .where(
            and_(
                AuthToken.user_id == user.id,
                AuthToken.type == TokenType.PASSWORD_RESET,
                AuthToken.used_at.is_(None),
            )
        )
        .values(used_at=now)
    )

    raw_token = secrets.token_urlsafe(32)

    token_record = AuthToken(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        type=TokenType.PASSWORD_RESET,
        expires_at=now + timedelta(minutes=PASSWORD_RESET_EXPIRY_MINUTES),
    )

    db.add(token_record)

    _send_password_reset_email(
        email = email,
        token = raw_token
    )

    db.commit()

    return raw_token


def reset_password(
    db: Session,
    token: str,
    new_password: str,
):
    now = datetime.now(UTC)

    token_record = db.scalar(
        select(AuthToken).where(
            and_(
                AuthToken.token_hash == hash_token(token),
                AuthToken.type == TokenType.PASSWORD_RESET,
            )
        )
    )

    if token_record is None:
        raise UnauthorizedError("Invalid password reset token")

    if token_record.used_at is not None:
        raise UnauthorizedError("Password reset token already used")

    if as_aware_utc(token_record.expires_at) <= now:
        raise UnauthorizedError("Password reset token expired")

    consumed = db.execute(
        update(AuthToken)
        .where(
            and_(
                AuthToken.id == token_record.id,
                AuthToken.used_at.is_(None),
            )
        )
        .values(used_at=now)
    )

    if consumed.rowcount != 1:
        db.rollback()
        raise UnauthorizedError("Invalid password reset token")

    user = db.get(User, token_record.user_id)

    if user is None:
        db.rollback()
        raise UnauthorizedError("User not found")

    user.password_hash = hash_password(new_password)

    db.execute(
        delete(RefreshToken)
        .where(RefreshToken.user_id == user.id)
    )

    db.commit()


def _send_password_reset_email(
    email: str,
    token: str,
) -> None:
    settings = get_settings()
    reset_url = (
        f"{settings.frontend_url}"
        f"/reset-password?token={token}"
    )

    html=f"""
    <html>
    <body>
        <p>We received a request to reset your password.</p>

        <p>
            Click the link below to set a new password:
        </p>

        <p>
            <a href="{reset_url}">
                Reset Password
            </a>
        </p>

        <p>
            This link will expire in 15 minutes.
        </p>

        <p>
            If you didn't request this, you can safely ignore this email.
        </p>
    </body>
    </html>
    """

    send_email(
        to = email, 
        subject = "Reset your password",
        html = html
    )
