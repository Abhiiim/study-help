from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.core.exceptions import UnauthorizedError
from app.api.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authorization token is required")

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid access token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid access token")

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid access token") from exc

    user = db.get(User, user_id_int)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return user
