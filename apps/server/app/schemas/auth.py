from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str | None = None
    device_info: str | None = Field(default=None, max_length=255)


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
    logout_all: bool = False


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(TokenPair):
    user: UserOut


class WebAuthResponse(AccessTokenResponse):
    user: UserOut


class GoogleStartResponse(BaseModel):
    authorize_url: str
    state: str


class GoogleSessionRequest(BaseModel):
    token: str = Field(min_length=1)


AuthClient = Literal["web", "extension"]
