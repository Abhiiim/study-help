from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tag import TagCreateRequest, TagListResponse, TagOut, TagUpdateRequest
from app.services.tag_service.create_tag import create_tag
from app.services.tag_service.delete_tag import delete_tag
from app.services.tag_service.list_tags import list_tags
from app.services.tag_service.update_tag import update_tag

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("/create_tag", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag_route(
    payload: TagCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TagOut:
    tag = create_tag(db, payload)
    return TagOut.model_validate(tag)


@router.get("/list_tags", response_model=TagListResponse)
def list_tags_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TagListResponse:
    items = list_tags(db)
    return TagListResponse(items=[TagOut.model_validate(item) for item in items])


@router.patch("/get_tag/{tag_id}", response_model=TagOut)
def update_tag_route(
    tag_id: int,
    payload: TagUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TagOut:
    tag = update_tag(db, tag_id, payload)
    return TagOut.model_validate(tag)


@router.delete("/delete/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_route(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_tag(db, tag_id)
