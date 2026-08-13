from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.resource import Resource
from app.models.user import User
from app.repositories.resource_repository import get_collections_by_ids, get_resource as fetch_resource, get_tags_by_ids
from app.schemas.resource import ResourceUpdateRequest


def update_resource(db: Session, user: User, resource_id: int, payload: ResourceUpdateRequest) -> Resource:
    resource = fetch_resource(db, user.id, resource_id)
    if resource is None:
        raise NotFoundError("Resource not found")

    if payload.title is not None:
        resource.title = payload.title

    if payload.is_deleted is not None:
        resource.is_deleted = payload.is_deleted
        if resource.is_deleted == True:
            resource.collections.clear()

    if payload.collection_ids is not None:
        resource.collections = get_collections_by_ids(db, user.id, payload.collection_ids)

    if payload.tag_ids is not None:
        resource.tags = get_tags_by_ids(db, payload.tag_ids)

    db.commit()
    db.refresh(resource)
    return resource
