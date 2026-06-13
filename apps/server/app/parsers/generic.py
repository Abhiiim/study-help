from html.parser import HTMLParser
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


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.description: str | None = None
        self.og_title: str | None = None
        self.og_description: str | None = None
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
            return

        if tag.lower() != "meta":
            return

        attr_map = {key.lower(): value for key, value in attrs if value is not None}
        name = attr_map.get("name", "").lower()
        prop = attr_map.get("property", "").lower()
        content = _clean_text(attr_map.get("content", ""))
        if not content:
            return

        if prop == "og:title":
            self.og_title = content
        elif prop == "og:description":
            self.og_description = content
        elif name == "description":
            self.description = content

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
            self.title = _clean_text("".join(self._title_parts))

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)


def _clean_text(value: str) -> str:
    return " ".join(value.split()).strip()


def parse_generic_metadata(html: str | None) -> tuple[str | None, str | None]:
    if not html:
        return None, None

    parser = _MetadataParser()
    parser.feed(html)
    title = parser.og_title or parser.title
    description = parser.og_description or parser.description
    return title, description
