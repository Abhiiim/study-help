from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.core.exceptions import ConflictError
from app.models.collection import Collection
from app.models.user import User
from app.schemas.collection import CollectionCreateRequest


def create_collection(db: Session, user: User, payload: CollectionCreateRequest) -> Collection:
    collection = Collection(
        user_id=user.id,
        name=payload.name.strip(),
        description=payload.description,
    )
    db.add(collection)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Collection could not be created") from exc

    db.refresh(collection)
    return collection
