from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.resource_repository import list_resources as list_resources_query


def list_resources(
    db: Session,
    user: User,
    *,
    search: str | None,
    platform: str | None,
    resource_type: str | None,
    collection_id: int | None,
    tag_id: int | None,
    page: int,
    limit: int,
):
    return list_resources_query(
        db,
        user.id,
        search=search,
        platform=platform,
        resource_type=resource_type,
        collection_id=collection_id,
        tag_id=tag_id,
        page=page,
        limit=limit,
    )
