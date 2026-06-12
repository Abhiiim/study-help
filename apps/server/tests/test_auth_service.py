from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.api.core.config import get_settings
from app.api.core.exceptions import BadRequestError, UnauthorizedError
from app.services import auth_service


def _google_state() -> str:
    settings = get_settings()
    return jwt.encode(
        {
            "type": "google_state",
            "nonce": "test-nonce",
            "exp": datetime.now(UTC) + timedelta(minutes=10),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


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
        state=_google_state(),
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
            state=_google_state(),
        )
