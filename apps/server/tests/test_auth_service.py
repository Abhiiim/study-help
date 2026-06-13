from datetime import UTC, datetime, timedelta

import pytest

from app.api.core.exceptions import BadRequestError, UnauthorizedError
from app.api.core.security import generate_jti, hash_token
from app.models.oauth_state import OAuthState
from app.services import auth_service

OAUTH_COOKIE_VALUE = "oauth-cookie"


def _google_state(db_session, client_type: str = "web") -> str:
    state = generate_jti()
    db_session.add(
        OAuthState(
            state_hash=hash_token(state),
            client_type=client_type,
            final_redirect_url="http://localhost:5173/oauth/callback",
            cookie_hash=hash_token(OAUTH_COOKIE_VALUE) if client_type == "web" else None,
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
        )
    )
    db_session.commit()
    return state


def test_signup_rejects_non_gmail(db_session):
    non_gmail = "alice" + "@example.com"
    with pytest.raises(BadRequestError):
        auth_service.signup(db_session, non_gmail, "strongpassword")


def test_refresh_rotation_revokes_old_token(db_session):
    gmail = "alice" + "@gmail.com"
    user, _, refresh_token = auth_service.signup(db_session, gmail, "strongpassword")

    _, _, new_refresh_token = auth_service.refresh_tokens(db_session, refresh_token)
    assert new_refresh_token != refresh_token

    with pytest.raises(UnauthorizedError):
        auth_service.refresh_tokens(db_session, refresh_token)

    # New token should still work once.
    _, _, third_refresh_token = auth_service.refresh_tokens(db_session, new_refresh_token)
    assert third_refresh_token != new_refresh_token


def test_logout_all_revokes_all_sessions(db_session):
    gmail = "alice" + "@gmail.com"
    user, _, refresh_token_one = auth_service.signup(db_session, gmail, "strongpassword")
    _, _, refresh_token_two = auth_service.login(db_session, gmail, "strongpassword")

    auth_service.logout(db_session, user, refresh_token=None, logout_all=True)

    with pytest.raises(UnauthorizedError):
        auth_service.refresh_tokens(db_session, refresh_token_one)

    with pytest.raises(UnauthorizedError):
        auth_service.refresh_tokens(db_session, refresh_token_two)


def test_google_callback_accepts_verified_gmail(db_session, monkeypatch):
    def fake_exchange_google_code(_: str) -> dict:
        return {
            "sub": "google-user-1",
            "email": "alice@gmail.com",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_service, "_exchange_google_code", fake_exchange_google_code)

    user, access_token, refresh_token = auth_service.google_callback(
        db_session,
        code="oauth-code",
        state=_google_state(db_session),
        cookie_value=OAUTH_COOKIE_VALUE,
    )

    assert user.email == "alice@gmail.com"
    assert user.google_sub == "google-user-1"
    assert access_token
    assert refresh_token


def test_google_callback_rejects_non_gmail(db_session, monkeypatch):
    def fake_exchange_google_code(_: str) -> dict:
        return {
            "sub": "google-user-2",
            "email": "alice@example.com",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_service, "_exchange_google_code", fake_exchange_google_code)

    with pytest.raises(BadRequestError):
        auth_service.google_callback(
            db_session,
            code="oauth-code",
            state=_google_state(db_session),
            cookie_value=OAUTH_COOKIE_VALUE,
        )


def test_google_login_token_exchanges_once(db_session, monkeypatch):
    def fake_exchange_google_code(_: str) -> dict:
        return {
            "sub": "google-user-3",
            "email": "alice@gmail.com",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_service, "_exchange_google_code", fake_exchange_google_code)

    login_token, _, _ = auth_service.create_google_login_token(
        db_session,
        code="oauth-code",
        state=_google_state(db_session),
        cookie_value=OAUTH_COOKIE_VALUE,
    )

    user, access_token, refresh_token = auth_service.exchange_google_login_token(db_session, login_token)

    assert user.email == "alice@gmail.com"
    assert access_token
    assert refresh_token

    with pytest.raises(UnauthorizedError):
        auth_service.exchange_google_login_token(db_session, login_token)


def test_google_state_exchanges_once(db_session, monkeypatch):
    def fake_exchange_google_code(_: str) -> dict:
        return {
            "sub": "google-user-4",
            "email": "alice@gmail.com",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_service, "_exchange_google_code", fake_exchange_google_code)

    state = _google_state(db_session)
    auth_service.create_google_login_token(
        db_session,
        code="oauth-code",
        state=state,
        cookie_value=OAUTH_COOKIE_VALUE,
    )

    with pytest.raises(UnauthorizedError):
        auth_service.create_google_login_token(
            db_session,
            code="oauth-code",
            state=state,
            cookie_value=OAUTH_COOKIE_VALUE,
        )


def test_google_state_requires_matching_cookie(db_session, monkeypatch):
    def fake_exchange_google_code(_: str) -> dict:
        return {
            "sub": "google-user-5",
            "email": "alice@gmail.com",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_service, "_exchange_google_code", fake_exchange_google_code)

    with pytest.raises(UnauthorizedError):
        auth_service.create_google_login_token(
            db_session,
            code="oauth-code",
            state=_google_state(db_session),
            cookie_value="wrong-cookie",
        )
