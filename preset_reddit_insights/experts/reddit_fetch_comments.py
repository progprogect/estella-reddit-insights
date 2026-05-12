$extens("include.py")
include("import json", [])
include("import random", [])
include("import time", [])
include("import requests", ["extella-pip install requests"])
include("from pathlib import Path", [])


def reddit_fetch_comments(
    listings_path: str = "",
    output_dir: str = "",
    app_user_agent: str = "",
    comments_engine: str = "C",
    max_posts_for_comments: int = 10,
    comment_limit: int = 100,
    min_delay_sec: float = 2.0,
    max_delay_sec: float = 4.0,
) -> dict:
    """Downloads comment trees for up to N posts using old.reddit (C) or www.reddit (B)."""
    print("[1/3] reddit_fetch_comments: validate...")
    if not listings_path:
        return {"status": "error", "message": "listings_path is required"}
    if not output_dir:
        return {"status": "error", "message": "output_dir is required"}

    lp = Path(listings_path).expanduser().resolve()
    if not lp.exists():
        return {"status": "error", "message": f"listings file not found: {lp}"}

    bundle = json.loads(lp.read_text(encoding="utf-8"))
    cfg = bundle.get("fetch_config") or {}
    ua = (app_user_agent or "").strip() or (str(cfg.get("app_user_agent", "")).strip())
    if not ua:
        return {"status": "error", "message": "app_user_agent is required (pass explicitly or in listings fetch_config)"}

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    comments_path = out_dir / "reddit_comments_raw.json"
    posts = bundle.get("posts", [])
    if not isinstance(posts, list) or not posts:
        empty = {"threads": []}
        comments_path.write_text(json.dumps(empty, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"status": "success", "comments_path": str(comments_path), "threads_count": 0, "note": "no posts"}

    eng = (comments_engine or "C").strip().upper()
    if eng not in ("B", "C"):
        return {"status": "error", "message": "comments_engine must be B or C"}

    cap = max(1, int(max_posts_for_comments))
    lim = min(500, max(1, int(comment_limit)))

    session = requests.Session()
    session.headers.update({"User-Agent": ua})

    def sleep_jitter() -> None:
        lo = float(min_delay_sec)
        hi = float(max_delay_sec)
        if hi < lo:
            lo, hi = hi, lo
        time.sleep(random.uniform(lo, hi))

    def fetch_thread(post_id: str) -> dict:
        if eng == "C":
            url = f"https://old.reddit.com/comments/{post_id}.json"
        else:
            url = f"https://www.reddit.com/comments/{post_id}.json"
        params = {"raw_json": "1", "limit": str(lim)}
        attempts = 0
        while attempts < 4:
            r = session.get(url, params=params, timeout=45)
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                wait_s = float(ra) if ra and str(ra).isdigit() else 60.0
                time.sleep(wait_s)
                attempts += 1
                continue
            if r.status_code >= 500:
                sleep_jitter()
                attempts += 1
                continue
            try:
                return {"post_id": post_id, "http": r.status_code, "json": r.json()}
            except Exception as e:
                return {"post_id": post_id, "http": r.status_code, "error": str(e), "text": r.text[:300]}

        return {"post_id": post_id, "http": 429, "error": "too_many_retries"}

    threads: list[dict] = []
    print("[2/3] fetching comment threads...")
    for i, p in enumerate(posts[:cap]):
        pid = (p or {}).get("id")
        if not pid:
            continue
        threads.append(fetch_thread(str(pid)))
        if i < cap - 1:
            sleep_jitter()

    payload = {"threads": threads}
    comments_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[3/3] done.")
    return {"status": "success", "comments_path": str(comments_path), "threads_count": len(threads), "engine": eng}
