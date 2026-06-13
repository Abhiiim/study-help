from app.db.base_class import Base

# Import models so metadata can discover them before create_all.
from app.models.oauth_state import OAuthState  # noqa: F401
from app.models.oauth_login_token import OAuthLoginToken  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.saved_item import SavedItem  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["Base"]
