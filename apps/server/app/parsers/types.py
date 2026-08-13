from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PreviewResult:
    title: str
    platform: str
    type: str
    thumbnail_url: str | None
    domain: str
    metadata: dict[str, Any] = field(default_factory=dict)
