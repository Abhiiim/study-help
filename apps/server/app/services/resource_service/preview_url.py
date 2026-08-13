from app.parsers.service import preview_url as parse_preview
from app.schemas.resource import PreviewURLResponse


def preview_url(url: str) -> PreviewURLResponse:
    result = parse_preview(url)
    return PreviewURLResponse(
        title=result.title,
        platform=result.platform,
        type=result.type,
        
        thumbnail_url=result.thumbnail_url,
    )
