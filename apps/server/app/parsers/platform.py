from urllib.parse import urlparse


def detect_platform_and_type(url: str) -> tuple[str, str]:
    domain = urlparse(url).netloc.lower().removeprefix("www.")

    if domain in {"leetcode.com", "leetcode.cn"} or domain.endswith(".leetcode.com"):
        return "leetcode", "problem"
    if domain in {"codeforces.com"} or domain.endswith(".codeforces.com"):
        return "codeforces", "problem"
    if domain in {"youtube.com", "youtu.be", "m.youtube.com"}:
        return "youtube", "video"
    if domain in {"medium.com", "substack.com"} or domain.endswith(".medium.com"):
        return domain.split(".")[0], "blog"
    if any(token in domain for token in ["docs.", "documentation", "readthedocs"]):
        return domain.split(".")[0] if "." in domain else domain, "documentation"

    return domain.split(".")[0] if "." in domain else domain, "blog"
