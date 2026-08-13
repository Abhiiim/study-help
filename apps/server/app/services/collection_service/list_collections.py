from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.resource_repository import list_collections as list_collections_query


#TODO: Need to add filters later on
def list_collections(db: Session, user: User):
    return list_collections_query(db, user.id)
