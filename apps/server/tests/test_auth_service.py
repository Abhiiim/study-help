import pytest

from app.api.core.exceptions import BadRequestError, UnauthorizedError
from app.services import auth_service


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
