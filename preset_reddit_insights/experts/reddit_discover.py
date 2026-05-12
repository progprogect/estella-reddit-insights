$extens("include.py")
include("import json", [])
include("import re", [])


def reddit_discover(
    method: str = "B",
    mode: str = "search",
    query: str = "",
    subreddit: str = "",
    sort: str = "new",
    time_filter: str = "week",
    max_pages: int = 5,
    limit_per_page: int = 100,
    min_delay_sec: float = 2.0,
    max_delay_sec: float = 4.0,
    fetch_comments: bool = False,
    max_posts_for_comments: int = 10,
    comment_limit: int = 100,
    comments_engine: str = "C",
    app_user_agent: str = "",
) -> dict:
    """Builds a fetch_config JSON-compatible dict for reddit_fetch_pages / reddit_fetch_comments."""
    m = (method or "").strip().upper()
    if m not in ("A", "B", "C"):
        return {"status": "error", "message": "method must be A, B, or C"}

    mode_norm = (mode or "").strip().lower()
    allowed_modes = ("search", "subreddit_hot", "subreddit_new")
    if mode_norm not in allowed_modes:
        return {"status": "error", "message": "mode must be one of: " + ", ".join(allowed_modes)}

    if mode_norm == "search" and not (query or "").strip():
        return {"status": "error", "message": "query is required for search mode"}

    if mode_norm in ("subreddit_hot", "subreddit_new") and not (subreddit or "").strip():
        return {"status": "error", "message": "subreddit is required for subreddit_* modes"}

    sub_clean = re.sub(r"^r/", "", (subreddit or "").strip())

    cfg = {
        "method": m,
        "mode": mode_norm,
        "query": (query or "").strip(),
        "subreddit": sub_clean,
        "sort": (sort or "new").strip(),
        "time_filter": (time_filter or "week").strip(),
        "max_pages": int(max_pages),
        "limit_per_page": min(int(limit_per_page), 100),
        "min_delay_sec": float(min_delay_sec),
        "max_delay_sec": float(max_delay_sec),
        "fetch_comments": bool(fetch_comments),
        "max_posts_for_comments": int(max_posts_for_comments),
        "comment_limit": min(int(comment_limit), 500),
        "comments_engine": (comments_engine or "C").strip().upper(),
        "app_user_agent": (app_user_agent or "").strip(),
    }

    return {"status": "success", "fetch_config": cfg, "fetch_config_json": json.dumps(cfg, ensure_ascii=False)}
