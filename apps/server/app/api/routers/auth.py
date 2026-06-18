from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, Body, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.core.auth import get_current_user
from app.api.core.config import get_settings
from app.api.core.exceptions import BadRequestError, UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthClient,
    AuthResponse,
    GoogleSessionRequest,
    GoogleStartResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SignupRequest,
    SignupResponse,
    UserOut,
    WebAuthResponse,
)

from app.services.auth_service.google_callback import create_google_login_token
from app.services.auth_service.google_start import generate_oauth_cookie_value, google_start
from app.services.auth_service.google_session import exchange_google_login_token
from app.services.auth_service.signup import signup
from app.services.auth_service.login import login
from app.services.auth_service.refresh_tokens import refresh_tokens
from app.services.auth_service.logout import logout_by_refresh_token
from app.services.auth_service.email_verification_service import verify_email

router = APIRouter(prefix="/auth", tags=["Auth"])


def _device_from_request(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent")
    return user_agent[:255] if user_agent else None


def _cookie_domain() -> str | None:
    return get_settings().cookie_domain or None


def _auth_cookie_path() -> str:
    settings = get_settings()
    return f"{settings.api_v1_prefix}/auth"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path=_auth_cookie_path(),
        domain=_cookie_domain(),
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _clear_refresh_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        settings.refresh_cookie_name,
        path=_auth_cookie_path(),
        domain=_cookie_domain(),
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _set_oauth_state_cookie(response: Response, cookie_value: str) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.oauth_state_cookie_name,
        cookie_value,
        max_age=10 * 60,
        path=_auth_cookie_path(),
        domain=_cookie_domain(),
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _clear_oauth_state_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        settings.oauth_state_cookie_name,
        path=_auth_cookie_path(),
        domain=_cookie_domain(),
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _build_auth_response(
    user: User,
    access_token: str,
    refresh_token: str,
    response: Response,
    client: AuthClient,
) -> AuthResponse | WebAuthResponse:
    if client == "extension":
        return AuthResponse(
            user=UserOut.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    _set_refresh_cookie(response, refresh_token)
    return WebAuthResponse(
        user=UserOut.model_validate(user),
        access_token=access_token,
    )


def _validated_extension_redirect_uri(value: str | None) -> str:
    if not value:
        raise BadRequestError("extension_redirect_uri is required", code="extension_redirect_uri_required")

    parsed = urlparse(value)
    origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else ""
    if origin not in get_settings().allowed_extension_redirect_origins:
        raise BadRequestError("Extension redirect URI is not allowed", code="extension_redirect_uri_not_allowed")
    return value


@router.post("/signup", response_model=SignupResponse)
def signup_route(
    payload: SignupRequest,
    db: Session = Depends(get_db),
):
    user = signup(
        db,
        payload.email,
        payload.password,
    )

    return SignupResponse(
        message="Verification email sent",
        email=user.email,
    )

@router.post("/login", response_model=AuthResponse | WebAuthResponse)
def login_route(
    payload: LoginRequest,
    request: Request,
    response: Response,
    client: AuthClient = Query(default="web"),
    db: Session = Depends(get_db),
) -> AuthResponse | WebAuthResponse:
    user, access_token, refresh_token = login(
        db,
        payload.email,
        payload.password,
        device_info=_device_from_request(request),
    )
    return _build_auth_response(user, access_token, refresh_token, response, client)


@router.get("/verify-email")
def verify_email_route(
    token: str,
    db: Session = Depends(get_db),
):
    verify_email(
        db=db,
        token=token,
    )

    settings = get_settings()

    return RedirectResponse(
        f"{settings.frontend_url}/login?verified=true"
    )


@router.get("/google/start", response_model=GoogleStartResponse)
def google_start_route(
    response: Response,
    client: AuthClient = Query(default="web"),
    extension_redirect_uri: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> GoogleStartResponse:
    if client == "extension":
        final_redirect_url = _validated_extension_redirect_uri(extension_redirect_uri)
        cookie_value = None
    else:
        final_redirect_url = get_settings().frontend_oauth_callback_url
        cookie_value = generate_oauth_cookie_value()

    authorize_url, state_value = google_start(
        db,
        client_type=client,
        final_redirect_url=final_redirect_url,
        cookie_value=cookie_value,
    )

    if cookie_value:
        _set_oauth_state_cookie(response, cookie_value)

    return GoogleStartResponse(authorize_url=authorize_url, state=state_value)


@router.get("/google/callback")
def google_callback_route(
    request: Request,
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    cookie_value = request.cookies.get(settings.oauth_state_cookie_name)
    login_token, final_redirect_url, client_type = create_google_login_token(
        db,
        code=code,
        state=state,
        cookie_value=cookie_value,
    )
    separator = "&" if "?" in final_redirect_url else "?"
    response = RedirectResponse(
        f"{final_redirect_url}{separator}{urlencode({'token': login_token})}",
        status_code=status.HTTP_302_FOUND,
    )
    if client_type == "web":
        _clear_oauth_state_cookie(response)
    return response


@router.post("/google/session", response_model=WebAuthResponse)
def google_session(
    payload: GoogleSessionRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> WebAuthResponse:
    user, access_token, refresh_token = exchange_google_login_token(
        db,
        token=payload.token,
        device_info=_device_from_request(request),
    )
    _set_refresh_cookie(response, refresh_token)
    return WebAuthResponse(user=UserOut.model_validate(user), access_token=access_token)


@router.post("/extension/google/session", response_model=AuthResponse)
def extension_google_session(
    payload: GoogleSessionRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user, access_token, refresh_token = exchange_google_login_token(
        db,
        token=payload.token,
        device_info=_device_from_request(request),
    )
    return AuthResponse(
        user=UserOut.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=AuthResponse | WebAuthResponse)
def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> AuthResponse | WebAuthResponse:
    provided_refresh_token = payload.refresh_token if payload else None
    refresh_token = provided_refresh_token or request.cookies.get(get_settings().refresh_cookie_name)
    if not refresh_token:
        raise UnauthorizedError("Refresh token is required")

    user, access_token, new_refresh_token = refresh_tokens(
        db,
        refresh_token,
        payload.device_info if payload else _device_from_request(request),
    )

    if provided_refresh_token:
        return AuthResponse(
            user=UserOut.model_validate(user),
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    _set_refresh_cookie(response, new_refresh_token)
    return WebAuthResponse(user=UserOut.model_validate(user), access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    payload: LogoutRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> None:
    provided_refresh_token = payload.refresh_token if payload else None
    refresh_token = provided_refresh_token or request.cookies.get(get_settings().refresh_cookie_name)
    logout_all = payload.logout_all if payload else False

    if refresh_token:
        logout_by_refresh_token(db, refresh_token=refresh_token, logout_all=logout_all)

    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
