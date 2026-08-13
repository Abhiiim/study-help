from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.resource import Resource
from app.models.user import User
from app.repositories.activity_repository import log_activity
from app.repositories.resource_repository import get_resource as fetch_resource


def mark_resource_opened(db: Session, user: User, resource_id: int) -> Resource:
    resource = fetch_resource(db, user.id, resource_id)
    if resource is None:
        raise NotFoundError("Resource not found")

    resource.last_opened_at = datetime.now(timezone.utc)
    log_activity(db, resource.id, "opened")
    db.commit()
    db.refresh(resource)
    return resource
