from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

ContentType = Literal["problem", "blog", "other"]
SortType = Literal["recent", "oldest"]


class ItemCreateRequest(BaseModel):
    url: HttpUrl
    is_favorite: bool = False
    note: str | None = Field(default=None, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=20)


class ItemUpdateRequest(BaseModel):
    is_favorite: bool | None = None
    note: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = Field(default=None, max_length=20)


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    url: str
    canonical_url: str
    source_site: str
    content_type: str
    title: str
    snippet: str | None
    metadata_json: dict[str, Any]
    is_favorite: bool
    note: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    items: list[ItemOut]
    total: int
    page: int
    limit: int


class SourceStat(BaseModel):
    site: str
    count: int


class ItemStatsResponse(BaseModel):
    saved_count: int
    favorite_count: int
    source_count: int
    top_sources: list[SourceStat]
