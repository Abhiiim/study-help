from datetime import timedelta, datetime
import secrets

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import EmailVerificationToken
from app.models import User
from app.api.core.security import hash_token
from app.api.core.config import get_settings
from apps.server.app.main import settings


def create_email_verification_token(db: Session, user: User):
    token = secrets.token_urlsafe(32)

    verification = EmailVerificationToken(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(verification)

    return token


def send_verification_email(
    user: User,
    token: str,
):
    settings = get_settings()

    verification_url = (
        f"{settings.frontend_url}"
        f"/verify-email?token={token}"
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
):
    token_hash = hash_token(token)

    verification = db.scalar(
        select(EmailVerificationToken)
        .where(
            EmailVerificationToken.token_hash == token_hash
        )
    )

    if verification is None:
        raise ValidationError("Invalid token")

    if verification.used_at:
        raise ValidationError("Already used")

    if verification.expires_at < datetime.utcnow():
        raise ValidationError("Expired token")

    verification.used_at = datetime.utcnow()

    user = verification.user
    user.is_email_verified = True
    user.email_verified_at = datetime.utcnow()

    db.commit()