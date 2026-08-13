from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.repositories.resource_repository import get_tag as fetch_tag


def delete_tag(db: Session, tag_id: int) -> None:
    tag = fetch_tag(db, tag_id)
    if tag is None:
        raise NotFoundError("Tag not found")

    db.delete(tag)
    db.commit()
