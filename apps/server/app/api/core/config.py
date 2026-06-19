from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "Study Saver API"
    env: Literal["development", "test", "production"] = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    database_url: str = ""

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    frontend_oauth_callback_url: str = "http://localhost:5173/oauth/callback"
    frontend_url: str = "http://localhost:5173"
    api_public_url: str = "http://localhost:8000"
    allowed_extension_redirect_origins: list[str] = Field(default_factory=list)

    refresh_cookie_name: str = "study_saver_refresh"
    oauth_state_cookie_name: str = "study_saver_oauth_state"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    cors_origin_regex: str | None = r"^chrome-extension://[a-z]{32}$"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    def validate_runtime_settings(self) -> None:
        errors: list[str] = []

        if self.env == "production":
            if self.debug:
                errors.append("DEBUG must be false in production")
            if not self.database_url:
                errors.append("DATABASE_URL is required in production")
            if self.jwt_secret_key in {"change-me", "replace-with-a-long-random-secret"} or len(self.jwt_secret_key) < 32:
                errors.append("JWT_SECRET_KEY must be a strong production secret")
            if not self.google_client_id or not self.google_client_secret:
                errors.append("Google OAuth credentials are required in production")
            if "*" in self.cors_origins:
                errors.append("CORS_ORIGINS cannot contain '*' in production")
            if self.cors_origin_regex in {"*", ".*", "^.*$"}:
                errors.append("CORS_ORIGIN_REGEX is too broad for production")
            if not self.cookie_secure:
                errors.append("COOKIE_SECURE must be true in production")
            if not self.allowed_extension_redirect_origins:
                errors.append("ALLOWED_EXTENSION_REDIRECT_ORIGINS is required in production")

        for name, value in {
            "GOOGLE_REDIRECT_URI": self.google_redirect_uri,
            "FRONTEND_OAUTH_CALLBACK_URL": self.frontend_oauth_callback_url,
            "FRONTEND_URL": self.frontend_url,
            "API_PUBLIC_URL": self.api_public_url,
        }.items():
            if not _is_http_url(value):
                errors.append(f"{name} must be an absolute http(s) URL")

        for origin in self.allowed_extension_redirect_origins:
            if not _is_origin(origin):
                errors.append(f"Invalid extension redirect origin: {origin}")

        if errors:
            raise RuntimeError("; ".join(errors))


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_origin(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and not parsed.path and not parsed.query


@lru_cache
def get_settings() -> Settings:
    return Settings()
