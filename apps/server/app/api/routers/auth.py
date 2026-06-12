from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.core.auth import get_current_user
from app.api.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    GoogleSessionRequest,
    GoogleStartResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SignupRequest,
    UserOut,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


def _device_from_request(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent")
    return user_agent[:255] if user_agent else None


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    user, access_token, refresh_token = auth_service.signup(
        db,
        payload.email,
        payload.password,
        device_info=_device_from_request(request),
    )
    return AuthResponse(
        user=UserOut.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    user, access_token, refresh_token = auth_service.login(
        db,
        payload.email,
        payload.password,
        device_info=_device_from_request(request),
    )
    return AuthResponse(
        user=UserOut.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/google/start", response_model=GoogleStartResponse)
def google_start() -> GoogleStartResponse:
    authorize_url, state_value = auth_service.google_start()
    return GoogleStartResponse(authorize_url=authorize_url, state=state_value)


@router.get("/google/callback")
def google_callback(
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    login_token = auth_service.create_google_login_token(
        db,
        code=code,
        state=state,
    )
    callback_url = get_settings().frontend_oauth_callback_url
    separator = "&" if "?" in callback_url else "?"
    return RedirectResponse(
        f"{callback_url}{separator}{urlencode({'token': login_token})}",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/google/session", response_model=AuthResponse)
def google_session(
    payload: GoogleSessionRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user, access_token, refresh_token = auth_service.exchange_google_login_token(
        db,
        token=payload.token,
        device_info=_device_from_request(request),
    )
    return AuthResponse(
        user=UserOut.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user, access_token, refresh_token = auth_service.refresh_tokens(
        db,
        payload.refresh_token,
        payload.device_info,
    )
    return AuthResponse(
        user=UserOut.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    auth_service.logout(
        db,
        user=current_user,
        refresh_token=payload.refresh_token,
        logout_all=payload.logout_all,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
