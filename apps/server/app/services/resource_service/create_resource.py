from sqlalchemy.orm import Session

from app.models.resource import Resource
from app.models.user import User
from app.parsers.service import preview_url as parse_preview
from app.repositories.activity_repository import log_activity
from app.repositories.resource_repository import get_collections_by_ids, get_resource_using_url, get_tags_by_ids
from app.schemas.resource import ResourceCreateRequest


def create_resource(db: Session, user: User, payload: ResourceCreateRequest) -> Resource:
    preview = parse_preview(str(payload.url))

    existing_resource = get_resource_using_url(db, user.id, payload.url)
    if (existing_resource):
        #TODO: Need to provide some message
        return existing_resource

    resource = Resource(
        user_id=user.id,
        url=str(payload.url),
        title=preview.title,
        type=preview.type,
        platform=preview.platform,
        domain=preview.domain,
        thumbnail_url=preview.thumbnail_url,
        metadata_=preview.metadata,
    )

    if payload.collection_ids:
        resource.collections = get_collections_by_ids(db, user.id, payload.collection_ids)

    if payload.tag_ids:
        resource.tags = get_tags_by_ids(db, payload.tag_ids)

    db.add(resource)
    db.flush()

    log_activity(db, resource.id, "created")
    db.commit()
    db.refresh(resource)
    return resource
