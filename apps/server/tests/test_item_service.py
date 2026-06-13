from app.parsers.types import ParserResult
from app.schemas.item import ItemCreateRequest, ItemUpdateRequest
from app.services import auth_service, item_service


def test_save_item_deduplicates_by_canonical_url(db_session, monkeypatch):
    gmail = "alice" + "@gmail.com"
    user, _, _ = auth_service.signup(db_session, gmail, "strongpassword")

    def fake_parse_url(_: str) -> ParserResult:
        return ParserResult(
            canonical_url="https://example.com/problem-a",
            source_site="example.com",
            content_type="problem",
            title="Problem A",
            snippet="Snippet",
            metadata_json={"fetched": True},
        )

    monkeypatch.setattr(item_service, "parse_url", fake_parse_url)

    first = item_service.save_item(
        db_session,
        user,
        ItemCreateRequest(url="https://example.com/problem-a?utm_source=test", tags=["dp"], note="first"),
    )
    second = item_service.save_item(
        db_session,
        user,
        ItemCreateRequest(url="https://example.com/problem-a?utm_campaign=test", tags=["graph"], note="updated"),
    )

    assert first.id == second.id
    assert second.note == "updated"
    assert second.tags == ["graph"]


def test_list_and_patch_item(db_session, monkeypatch):
    gmail = "alice" + "@gmail.com"
    user, _, _ = auth_service.signup(db_session, gmail, "strongpassword")

    def fake_parse_url(url: str) -> ParserResult:
        return ParserResult(
            canonical_url=url,
            source_site="medium.com",
            content_type="blog",
            title="A Blog Post",
            snippet="A short snippet",
            metadata_json={"fetched": False},
        )

    monkeypatch.setattr(item_service, "parse_url", fake_parse_url)

    item = item_service.save_item(
        db_session,
        user,
        ItemCreateRequest(url="https://medium.com/@x/post", is_favorite=False),
    )

    patched = item_service.update_item(
        db_session,
        user,
        item.id,
        ItemUpdateRequest(is_favorite=True, tags=["reading", "reading", "algorithms"]),
    )
    assert patched.is_favorite is True
    assert patched.tags == ["reading", "algorithms"]

    items, total = item_service.list_items(
        db_session,
        user,
        q="blog",
        source_site="medium.com",
        content_type="blog",
        is_favorite=True,
        page=1,
        limit=10,
        sort="recent",
    )

    assert total == 1
    assert len(items) == 1


def test_item_stats_are_scoped_to_user(db_session, monkeypatch):
    first_user, _, _ = auth_service.signup(db_session, "alice@gmail.com", "strongpassword")
    second_user, _, _ = auth_service.signup(db_session, "bob@gmail.com", "strongpassword")

    def fake_parse_url(url: str) -> ParserResult:
        source = "leetcode.com" if "leetcode" in url else "medium.com"
        return ParserResult(
            canonical_url=url,
            source_site=source,
            content_type="problem" if source == "leetcode.com" else "blog",
            title=url,
            snippet=None,
            metadata_json={"fetched": False},
        )

    monkeypatch.setattr(item_service, "parse_url", fake_parse_url)

    item_service.save_item(
        db_session,
        first_user,
        ItemCreateRequest(url="https://leetcode.com/problems/a", is_favorite=True),
    )
    item_service.save_item(
        db_session,
        first_user,
        ItemCreateRequest(url="https://medium.com/post"),
    )
    item_service.save_item(
        db_session,
        second_user,
        ItemCreateRequest(url="https://leetcode.com/problems/b", is_favorite=True),
    )

    stats = item_service.get_item_stats(db_session, first_user)

    assert stats["saved_count"] == 2
    assert stats["favorite_count"] == 1
    assert stats["source_count"] == 2
    assert stats["top_sources"][0]["count"] == 1
