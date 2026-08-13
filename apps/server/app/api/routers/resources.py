from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.resource import (
    PreviewURLRequest,
    PreviewURLResponse,
    ResourceCreateRequest,
    ResourceListResponse,
    ResourceOut,
    ResourceUpdateRequest,
)
from app.services.resource_service.create_resource import create_resource
from app.services.resource_service.delete_resource import delete_resource
from app.services.resource_service.get_resource import get_resource
from app.services.resource_service.list_resources import list_resources
from app.services.resource_service.mark_resource_opened import mark_resource_opened
from app.services.resource_service.preview_url import preview_url
from app.services.resource_service.update_resource import update_resource

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("/preview", response_model=PreviewURLResponse)
def preview_resource_url(
    payload: PreviewURLRequest,
    _: User = Depends(get_current_user),
) -> PreviewURLResponse:
    return preview_url(str(payload.url))


@router.post("/create_resource", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource_route(
    payload: ResourceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceOut:
    resource = create_resource(db, current_user, payload)
    return ResourceOut.model_validate(resource)


@router.get("/list_resources", response_model=ResourceListResponse)
def list_resources_route(
    search: str | None = Query(default=None),
    platform: str | None = Query(default=None),
    type: str | None = Query(default=None),
    collection_id: int | None = Query(default=None),
    tag_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceListResponse:
    items, total = list_resources(
        db,
        current_user,
        search=search,
        platform=platform,
        resource_type=type,
        collection_id=collection_id,
        tag_id=tag_id,
        page=page,
        limit=limit,
    )
    return ResourceListResponse(
        items=[ResourceOut.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/get_resource/{resource_id}", response_model=ResourceOut)
def get_resource_route(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceOut:
    resource = get_resource(db, current_user, resource_id)
    return ResourceOut.model_validate(resource)


@router.patch("/update_resource/{resource_id}", response_model=ResourceOut)
def update_resource_route(
    resource_id: int,
    payload: ResourceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceOut:
    resource = update_resource(db, current_user, resource_id, payload)
    return ResourceOut.model_validate(resource)


@router.delete("/delete_resource/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource_route(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_resource(db, current_user, resource_id)


@router.post("/mark_resource_open/{resource_id}", response_model=ResourceOut)
def mark_resource_opened_route(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceOut:
    resource = mark_resource_opened(db, current_user, resource_id)
    return ResourceOut.model_validate(resource)
