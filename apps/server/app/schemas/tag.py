from pydantic import BaseModel, ConfigDict, Field


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TagListResponse(BaseModel):
    items: list[TagOut]
