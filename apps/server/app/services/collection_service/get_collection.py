from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.collection import Collection
from app.models.user import User
from app.repositories.resource_repository import get_collection as fetch_collection


def get_collection(db: Session, user: User, collection_id: int) -> Collection:
    collection = fetch_collection(db, user.id, collection_id)
    if collection is None:
        raise NotFoundError("Collection not found")
    return collection
