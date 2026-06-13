import ipaddress
import logging
import socket
from urllib.parse import urljoin, urlparse

import httpx

from app.parsers.adapters import infer_content_type
from app.parsers.generic import canonicalize_url, parse_generic_metadata, source_from_url
from app.parsers.types import ParserResult

logger = logging.getLogger(__name__)

MAX_REDIRECTS = 3
MAX_METADATA_BYTES = 256 * 1024
ALLOWED_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}


def _host_is_public(host: str, port: int | None) -> bool:
    if host.lower() in {"localhost", "localhost."} or host.lower().endswith(".localhost"):
        return False

    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    if not addresses:
        return False

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            return False

    return True


def _is_fetchable_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return _host_is_public(parsed.hostname, port)


def _response_is_html(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    return content_type in ALLOWED_CONTENT_TYPES or content_type.endswith("+html")


def _read_limited_text(response: httpx.Response) -> str | None:
    chunks: list[bytes] = []
    total = 0

    for chunk in response.iter_bytes():
        total += len(chunk)
        if total > MAX_METADATA_BYTES:
            return None
        chunks.append(chunk)

    encoding = response.encoding or "utf-8"
    return b"".join(chunks).decode(encoding, errors="replace")


def _fetch_html(url: str) -> str | None:
    current_url = url
    try:
        with httpx.Client(timeout=5.0, follow_redirects=False, trust_env=False) as client:
            for _ in range(MAX_REDIRECTS + 1):
                if not _is_fetchable_url(current_url):
                    return None

                with client.stream("GET", current_url, headers={"User-Agent": "StudySaverBot/0.1"}) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            return None
                        current_url = urljoin(current_url, location)
                        continue

                    if response.status_code >= 400 or not _response_is_html(response):
                        return None

                    return _read_limited_text(response)
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
