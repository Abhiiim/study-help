from sqlalchemy.orm import Session

from app.repositories.resource_repository import list_tags as list_tags_query


def list_tags(db: Session):
    return list_tags_query(db)
