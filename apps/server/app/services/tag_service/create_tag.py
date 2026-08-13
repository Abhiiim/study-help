from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.core.exceptions import ConflictError
from app.models.tag import Tag
from app.schemas.tag import TagCreateRequest


def create_tag(db: Session, payload: TagCreateRequest) -> Tag:
    name = payload.name.strip()
    existing = db.scalar(select(Tag).where(Tag.name == name))
    if existing is not None:
        return existing

    tag = Tag(name=name)
    db.add(tag)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        existing = db.scalar(select(Tag).where(Tag.name == name))
        if existing is not None:
            return existing
        raise ConflictError("Tag could not be created") from exc

    db.refresh(tag)
    return tag
