import logging

import httpx

from app.parsers.adapters import infer_content_type
from app.parsers.generic import canonicalize_url, parse_generic_metadata, source_from_url
from app.parsers.types import ParserResult

logger = logging.getLogger(__name__)


def _fetch_html(url: str) -> str | None:
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            response = client.get(url)
            if response.status_code >= 400:
                return None
            return response.text
    except Exception:
        logger.info("Metadata fetch failed for %s", url)
        return None


def parse_url(url: str) -> ParserResult:
    canonical_url = canonicalize_url(url)
    source_site = source_from_url(canonical_url)

    html = _fetch_html(canonical_url)
    title, snippet = parse_generic_metadata(html)

    fallback_title = canonical_url
    resolved_title = title or fallback_title
    content_type = infer_content_type(source_site=source_site, title=resolved_title)

    return ParserResult(
        canonical_url=canonical_url,
        source_site=source_site,
        content_type=content_type,
        title=resolved_title[:500],
        snippet=snippet[:1000] if snippet else None,
        metadata_json={
            "fetched": html is not None,
        },
    )
