from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.collection import (
    CollectionCreateRequest,
    CollectionListResponse,
    CollectionOut,
    CollectionUpdateRequest,
)
from app.services.collection_service.create_collection import create_collection
from app.services.collection_service.delete_collection import delete_collection
from app.services.collection_service.get_collection import get_collection
from app.services.collection_service.list_collections import list_collections
from app.services.collection_service.update_collection import update_collection

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post("/create_collection", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
def create_collection_route(
    payload: CollectionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionOut:
    collection = create_collection(db, current_user, payload)
    return CollectionOut.model_validate(collection)


@router.get("/list_collections", response_model=CollectionListResponse)
def list_collections_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionListResponse:
    items = list_collections(db, current_user)
    return CollectionListResponse(items=[CollectionOut.model_validate(item) for item in items])


@router.get("/get_collection/{collection_id}", response_model=CollectionOut)
def get_collection_route(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionOut:
    collection = get_collection(db, current_user, collection_id)
    return CollectionOut.model_validate(collection)


@router.patch("/update_collection/{collection_id}", response_model=CollectionOut)
def update_collection_route(
    collection_id: int,
    payload: CollectionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionOut:
    collection = update_collection(db, current_user, collection_id, payload)
    return CollectionOut.model_validate(collection)


@router.delete("/delete_collection/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_route(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_collection(db, current_user, collection_id)
