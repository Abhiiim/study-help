from app.db.base_class import Base

# Import models so metadata can discover them before create_all.
from app.models.activity import Activity  # noqa: F401
from app.models.auth_token import AuthToken  # noqa: F401
from app.models.collection import Collection  # noqa: F401
from app.models.oauth_state import OAuthState  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.resource import Resource  # noqa: F401
from app.models.resource_collection import ResourceCollection  # noqa: F401
from app.models.resource_tag import ResourceTag  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["Base"]
