from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.core.exceptions import ConflictError, NotFoundError
from app.models.tag import Tag
from app.repositories.resource_repository import get_tag as fetch_tag
from app.schemas.tag import TagUpdateRequest


def update_tag(db: Session, tag_id: int, payload: TagUpdateRequest) -> Tag:
    tag = fetch_tag(db, tag_id)
    if tag is None:
        raise NotFoundError("Tag not found")

    name = payload.name.strip()
    existing = db.scalar(select(Tag).where(Tag.name == name, Tag.id != tag_id))
    if existing is not None:
        raise ConflictError("Tag name already exists", code="tag_exists")

    tag.name = name

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Tag name already exists", code="tag_exists") from exc

    db.refresh(tag)
    return tag
