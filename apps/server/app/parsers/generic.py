import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
}


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    query_pairs = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in TRACKING_QUERY_KEYS]
    clean_query = urlencode(query_pairs, doseq=True)

    clean = parsed._replace(fragment="", query=clean_query, netloc=netloc)
    return urlunparse(clean)


def source_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    host = host.removeprefix("www.")
    return host or "unknown"


def content_type_from_source(source_site: str) -> str:
    coding_sites = {
        "codeforces.com",
        "codechef.com",
        "leetcode.com",
        "atcoder.jp",
        "geeksforgeeks.org",
    }
    blog_sites = {"medium.com", "substack.com"}

    if any(source_site == site or source_site.endswith(f".{site}") for site in coding_sites):
        return "problem"
    if any(source_site == site or source_site.endswith(f".{site}") for site in blog_sites):
        return "blog"
    return "other"


def _find_title(html: str) -> str | None:
    patterns = [
        r'<meta\s+property="og:title"\s+content="([^"]+)"',
        r"<meta\s+property='og:title'\s+content='([^']+)'",
        r"<title>(.*?)</title>",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return None


def _find_description(html: str) -> str | None:
    patterns = [
        r'<meta\s+name="description"\s+content="([^"]+)"',
        r'<meta\s+property="og:description"\s+content="([^"]+)"',
        r"<meta\s+name='description'\s+content='([^']+)'",
        r"<meta\s+property='og:description'\s+content='([^']+)'",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return None


def parse_generic_metadata(html: str | None) -> tuple[str | None, str | None]:
    if not html:
        return None, None
    title = _find_title(html)
    description = _find_description(html)
    return title, description
