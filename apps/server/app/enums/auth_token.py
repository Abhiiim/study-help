from enum import Enum


class TokenType(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    OAUTH_LOGIN = "oauth_login"
    EMAIL_CHANGE = "email_change"