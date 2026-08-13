from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class PreviewURLRequest(BaseModel):
    url: HttpUrl


class PreviewURLResponse(BaseModel):
    title: str
    platform: str
    type: str
    difficulty: str | None = None
    thumbnail_url: str | None = None


class ResourceCreateRequest(BaseModel):
    url: HttpUrl
    collection_ids: list[int] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)


class ResourceUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    collection_ids: list[int] | None = None
    tag_ids: list[int] | None = None
    is_deleted: bool | None = None


class TagSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CollectionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    url: str
    title: str
    type: str
    platform: str
    domain: str
    thumbnail_url: str | None
    metadata: dict[str, Any] = Field(alias="metadata_")
    created_at: datetime
    updated_at: datetime
    last_opened_at: datetime | None
    tags: list[TagSummary] = Field(default_factory=list)
    collections: list[CollectionSummary] = Field(default_factory=list)


class ResourceListResponse(BaseModel):
    items: list[ResourceOut]
    total: int
    page: int
    limit: int
