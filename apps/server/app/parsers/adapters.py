from app.parsers.generic import content_type_from_source


def infer_content_type(source_site: str, title: str | None = None) -> str:
    inferred = content_type_from_source(source_site)
    if inferred != "other":
        return inferred

    # Lightweight heuristic for unknown sources.
    lowered = (title or "").lower()
    if any(token in lowered for token in ["problem", "contest", "leetcode", "codeforces"]):
        return "problem"
    if any(token in lowered for token in ["blog", "article", "post", "guide"]):
        return "blog"
    return "other"
