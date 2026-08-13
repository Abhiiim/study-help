from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.collection import Collection
from app.models.user import User
from app.repositories.resource_repository import get_collection as fetch_collection
from app.schemas.collection import CollectionUpdateRequest


def update_collection(db: Session, user: User, collection_id: int, payload: CollectionUpdateRequest) -> Collection:
    collection = fetch_collection(db, user.id, collection_id)
    if collection is None:
        raise NotFoundError("Collection not found")

    if payload.name is not None:
        collection.name = payload.name.strip()

    if payload.is_deleted is not None:
        collection.is_deleted = payload.is_deleted
        if payload.is_deleted == True:
            collection.resources.clear()

    if payload.description is not None:
        collection.description = payload.description

    db.commit()
    db.refresh(collection)
    return collection
