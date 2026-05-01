from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParserResult:
    canonical_url: str
    source_site: str
    content_type: str
    title: str
    snippet: str | None
    metadata_json: dict[str, Any] = field(default_factory=dict)
