from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.resource import Resource
from app.models.user import User
from app.repositories.resource_repository import get_resource as fetch_resource


def get_resource(db: Session, user: User, resource_id: int) -> Resource:
    resource = fetch_resource(db, user.id, resource_id)
    if resource is None:
        raise NotFoundError("Resource not found")
    return resource
