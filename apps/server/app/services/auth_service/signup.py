from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.core.exceptions import ConflictError
from app.api.core.security import hash_password
from app.models.user import User
from app.helpers.auth_helper import ensure_gmail, normalize_email
from app.services.auth_service.email_verification_service import create_email_verification_token, send_verification_email


def signup(db: Session, email: str, password: str, device_info: str | None = None) -> User:
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

    token = create_email_verification_token(db, user)

    send_verification_email(user, token)

    db.commit()

    return user
