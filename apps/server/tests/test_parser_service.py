from app.parsers import service


class _FakeStreamResponse:
    def __init__(self, *, status_code=200, headers=None, chunks=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._chunks = chunks or []
        self.encoding = "utf-8"

    @property
    def is_redirect(self):
        return self.status_code in {301, 302, 303, 307, 308}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def iter_bytes(self):
        yield from self._chunks


class _FakeClient:
    def __init__(self, responses):
        self._responses = list(responses)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def stream(self, *_args, **_kwargs):
        return self._responses.pop(0)


def test_private_urls_are_not_fetched(monkeypatch):
    def fail_getaddrinfo(*_args, **_kwargs):
        raise AssertionError("localhost should be rejected before DNS lookup")

    monkeypatch.setattr(service.socket, "getaddrinfo", fail_getaddrinfo)

    result = service.parse_url("http://localhost/admin")

    assert result.metadata_json["fetched"] is False
    assert result.title == "http://localhost/admin"


def test_private_ip_resolution_is_blocked(monkeypatch):
    monkeypatch.setattr(
        service.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(None, None, None, None, ("10.0.0.5", 80))],
    )

    assert service._is_fetchable_url("http://example.com") is False


def test_public_ip_resolution_is_allowed(monkeypatch):
    monkeypatch.setattr(
        service.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(None, None, None, None, ("93.184.216.34", 443))],
    )

    assert service._is_fetchable_url("https://example.com") is True


def test_html_parser_prefers_open_graph_metadata():
    html = """
    <html>
      <head>
        <title>Plain title</title>
        <meta name="description" content="Plain description">
        <meta property="og:title" content="OG title">
        <meta property="og:description" content="OG description">
      </head>
    </html>
    """

    title, description = service.parse_generic_metadata(html)

    assert title == "OG title"
    assert description == "OG description"


def test_redirect_to_private_target_is_blocked(monkeypatch):
    seen_urls = []

    def fake_is_fetchable(url):
        seen_urls.append(url)
        return url == "https://example.com/start"

    monkeypatch.setattr(service, "_is_fetchable_url", fake_is_fetchable)
    monkeypatch.setattr(
        service.httpx,
        "Client",
        lambda **_kwargs: _FakeClient(
            [
                _FakeStreamResponse(status_code=302, headers={"location": "http://10.0.0.5/admin"}),
            ]
        ),
    )

    assert service._fetch_html("https://example.com/start") is None
    assert seen_urls == ["https://example.com/start", "http://10.0.0.5/admin"]


def test_oversized_metadata_response_is_rejected(monkeypatch):
    monkeypatch.setattr(service, "MAX_METADATA_BYTES", 4)

    response = _FakeStreamResponse(
        headers={"content-type": "text/html"},
        chunks=[b"abc", b"de"],
    )

    assert service._read_limited_text(response) is None


def test_public_html_response_is_parsed(monkeypatch):
    monkeypatch.setattr(service, "_is_fetchable_url", lambda _url: True)
    monkeypatch.setattr(
        service.httpx,
        "Client",
        lambda **_kwargs: _FakeClient(
            [
                _FakeStreamResponse(
                    headers={"content-type": "text/html; charset=utf-8"},
                    chunks=[b"<html><head><title>Example Problem</title></head></html>"],
                ),
            ]
        ),
    )

    result = service.parse_url("https://example.com/problem")

    assert result.metadata_json["fetched"] is True
    assert result.title == "Example Problem"
