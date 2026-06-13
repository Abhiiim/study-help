from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.item import ItemCreateRequest, ItemListResponse, ItemOut, ItemStatsResponse, ItemUpdateRequest
from app.services import item_service

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = item_service.save_item(db, current_user, payload)
    return ItemOut.model_validate(item)


@router.get("", response_model=ItemListResponse)
def get_items(
    q: str | None = Query(default=None),
    source_site: str | None = Query(default=None),
    content_type: Literal["problem", "blog", "other"] | None = Query(default=None),
    is_favorite: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort: Literal["recent", "oldest"] = Query(default="recent"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemListResponse:
    items, total = item_service.list_items(
        db,
        current_user,
        q=q,
        source_site=source_site,
        content_type=content_type,
        is_favorite=is_favorite,
        page=page,
        limit=limit,
        sort=sort,
    )
    return ItemListResponse(
        items=[ItemOut.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/stats", response_model=ItemStatsResponse)
def get_item_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemStatsResponse:
    return ItemStatsResponse.model_validate(item_service.get_item_stats(db, current_user))


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = item_service.get_item_or_404(db, current_user, item_id)
    return ItemOut.model_validate(item)


@router.patch("/{item_id}", response_model=ItemOut)
def patch_item(
    item_id: int,
    payload: ItemUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = item_service.update_item(db, current_user, item_id, payload)
    return ItemOut.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item_service.delete_item(db, current_user, item_id)
