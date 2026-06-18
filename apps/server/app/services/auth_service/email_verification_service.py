from datetime import UTC, datetime, timedelta
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.core.config import get_settings
from app.api.core.exceptions import BadRequestError
from app.api.core.security import hash_token
from app.helpers.auth_helper import as_aware_utc
from app.models import EmailVerificationToken, User
from app.services.notification_service.email_service import send_email


def create_email_verification_token(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)

    verification = EmailVerificationToken(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db.add(verification)

    return token


def send_verification_email(
    user: User,
    token: str,
) -> None:
    settings = get_settings()

    verification_url = (
        f"{settings.api_public_url.rstrip('/')}"
        f"{settings.api_v1_prefix}/auth/verify-email?token={token}"
    )

    html = f"""
    <h2>Verify your email</h2>

    <p>Thanks for signing up.</p>

    <p>
        <a href="{verification_url}">
            Verify Email
        </a>
    </p>

    <p>This link expires in 24 hours.</p>
    """

    send_email(
        to=user.email,
        subject="Verify your email",
        html=html,
    )


def verify_email(
    db: Session,
    token: str,
) -> None:
    token_hash = hash_token(token)

    verification = db.scalar(
        select(EmailVerificationToken)
        .where(
            EmailVerificationToken.token_hash == token_hash
        )
    )

    if verification is None:
        raise BadRequestError("Invalid verification token", code="invalid_verification_token")

    if verification.used_at:
        raise BadRequestError("Verification token was already used", code="verification_token_used")

    now = datetime.now(UTC)
    if as_aware_utc(verification.expires_at) < now:
        raise BadRequestError("Verification token has expired", code="verification_token_expired")

    verification.used_at = now

    user = verification.user
    user.is_email_verified = True
    user.email_verified_at = now

    db.commit()
