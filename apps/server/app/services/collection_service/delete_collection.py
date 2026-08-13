from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.resource_repository import get_collection as fetch_collection


def delete_collection(db: Session, user: User, collection_id: int) -> None:
    collection = fetch_collection(db, user.id, collection_id)
    if collection is None:
        raise NotFoundError("Collection not found")

    db.delete(collection)
    db.commit()
