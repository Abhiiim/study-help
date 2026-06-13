from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.core.security import generate_jti, hash_token
from app.db.session import get_db
from app.main import app
from app.models.oauth_state import OAuthState
from app.services import auth_service

OAUTH_COOKIE_VALUE = "oauth-cookie"


@pytest.fixture
def api_client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _google_state(db_session) -> str:
    state = generate_jti()
    db_session.add(
        OAuthState(
            state_hash=hash_token(state),
            client_type="web",
            final_redirect_url="http://localhost:5173/oauth/callback",
            cookie_hash=hash_token(OAUTH_COOKIE_VALUE),
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
        )
    )
    db_session.commit()
    return state


def test_web_auth_uses_refresh_cookie(api_client):
    signup_response = api_client.post(
        "/api/v1/auth/signup",
        json={"email": "alice@gmail.com", "password": "strongpassword"},
    )

    assert signup_response.status_code == 201
    assert "refresh_token" not in signup_response.json()
    assert "study_saver_refresh" in signup_response.headers["set-cookie"]

    refresh_response = api_client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    assert "refresh_token" not in refresh_response.json()

    access_token = refresh_response.json()["access_token"]
    me_response = api_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@gmail.com"

    logout_response = api_client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204

    expired_response = api_client.post("/api/v1/auth/refresh")
    assert expired_response.status_code == 401


def test_extension_login_returns_refresh_token(api_client, db_session):
    auth_service.signup(db_session, "alice@gmail.com", "strongpassword")

    login_response = api_client.post(
        "/api/v1/auth/login?client=extension",
        json={"email": "alice@gmail.com", "password": "strongpassword"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["refresh_token"]


def test_google_callback_redirects_with_one_time_token(api_client, db_session, monkeypatch):
    def fake_exchange_google_code(_: str) -> dict:
        return {
            "sub": "google-user-1",
            "email": "alice@gmail.com",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_service, "_exchange_google_code", fake_exchange_google_code)

    state = _google_state(db_session)
    api_client.cookies.set("study_saver_oauth_state", OAUTH_COOKIE_VALUE, domain="testserver.local", path="/api/v1/auth")

    response = api_client.get(
        f"/api/v1/auth/google/callback?code=oauth-code&state={state}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"].startswith("http://localhost:5173/oauth/callback?token=")

    replay_response = api_client.get(
        f"/api/v1/auth/google/callback?code=oauth-code&state={state}",
        follow_redirects=False,
    )
    assert replay_response.status_code == 401
