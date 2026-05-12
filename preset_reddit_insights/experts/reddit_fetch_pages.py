$extens("include.py")
include("import base64", [])
include("import json", [])
include("import random", [])
include("import time", [])
include("import requests", ["extella-pip install requests"])
include("from pathlib import Path", [])


def reddit_fetch_pages(
    fetch_config_json: str = "",
    output_dir: str = "",
    reddit_client_id: str = "",
    reddit_client_secret: str = "",
    app_user_agent: str = "",
) -> dict:
    """Fetches listing pages (search or subreddit) for methods A or B; writes JSON artifact for downstream steps."""
    print("[1/4] reddit_fetch_pages: validate...")

    if not fetch_config_json:
        return {"status": "error", "message": "fetch_config_json is required"}
    if not output_dir:
        return {"status": "error", "message": "output_dir is required"}

    try:
        cfg = json.loads(fetch_config_json)
    except Exception as e:
        return {"status": "error", "message": "invalid fetch_config_json: " + str(e)}

    ua = (app_user_agent or "").strip() or (str(cfg.get("app_user_agent", "")).strip())
    if not ua:
        return {"status": "error", "message": "app_user_agent is required (pass explicitly or inside fetch_config_json)"}

    method = str(cfg.get("method", "B")).upper()
    if method == "C":
        method = "B"
    if method not in ("A", "B"):
        return {"status": "error", "message": "unsupported listing method"}

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    listings_path = out_dir / "reddit_listings_posts.json"

    session = requests.Session()
    session.headers.update({"User-Agent": ua})

    def sleep_jitter() -> None:
        lo = float(cfg.get("min_delay_sec", 2.0))
        hi = float(cfg.get("max_delay_sec", 4.0))
        if hi < lo:
            lo, hi = hi, lo
        time.sleep(random.uniform(lo, hi))

    def request_with_retries(url: str, params: dict) -> tuple[int, object]:
        attempts = 0
        while attempts < 4:
            resp = session.get(url, params=params, timeout=45)
            if resp.status_code == 429:
                ra = resp.headers.get("Retry-After")
                wait_s = float(ra) if ra and str(ra).isdigit() else 60.0
                print(f"[warn] 429, sleeping {wait_s}s ...")
                time.sleep(wait_s)
                attempts += 1
                continue
            if resp.status_code >= 500:
                sleep_jitter()
                attempts += 1
                continue
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, {"_parse_error": True, "text": resp.text[:500]}

        return 429, {"error": "too_many_retries"}

    if method == "A":
        if not reddit_client_id or not reddit_client_secret:
            return {"status": "error", "message": "reddit_client_id and reddit_client_secret required for method A"}
        print("[2/4] OAuth client_credentials...")
        basic = base64.b64encode(
            (reddit_client_id + ":" + reddit_client_secret).encode("utf-8")
        ).decode("ascii")
        tr = session.post(
            "https://www.reddit.com/api/v1/access_token",
            headers={"Authorization": "Basic " + basic},
            data={"grant_type": "client_credentials"},
            timeout=30,
        )
        if tr.status_code != 200:
            return {
                "status": "error",
                "message": "token request failed: HTTP " + str(tr.status_code),
                "body": tr.text[:500],
            }
        token = tr.json().get("access_token")
        if not token:
            return {"status": "error", "message": "no access_token in token response"}
        session.headers["Authorization"] = "bearer " + token

    posts: list[dict] = []
    mode = str(cfg.get("mode", "search"))
    max_pages = max(1, int(cfg.get("max_pages", 5)))
    limit = min(100, max(1, int(cfg.get("limit_per_page", 100))))
    after = None

    print("[3/4] paging listings...")
    for page in range(max_pages):
        params = {"raw_json": "1", "limit": str(limit)}
        if after:
            params["after"] = after

        if mode == "search":
            params["q"] = cfg.get("query", "")
            params["sort"] = cfg.get("sort", "new")
            params["t"] = cfg.get("time_filter", "week")
            params["type"] = "link"
            params["restrict_sr"] = "0"
            if method == "A":
                url = "https://oauth.reddit.com/search.json"
            else:
                url = "https://www.reddit.com/search.json"
        elif mode == "subreddit_hot":
            sub = cfg.get("subreddit", "")
            if method == "A":
                url = f"https://oauth.reddit.com/r/{sub}/hot.json"
            else:
                url = f"https://www.reddit.com/r/{sub}/hot.json"
        elif mode == "subreddit_new":
            sub = cfg.get("subreddit", "")
            if method == "A":
                url = f"https://oauth.reddit.com/r/{sub}/new.json"
            else:
                url = f"https://www.reddit.com/r/{sub}/new.json"
        else:
            return {"status": "error", "message": "unsupported mode"}

        code, data = request_with_retries(url, params)
        if code != 200:
            return {"status": "error", "message": f"listing HTTP {code}", "page": page, "url": url}

        if not isinstance(data, dict) or "data" not in data:
            return {"status": "error", "message": "unexpected listing JSON shape", "page": page}

        children = data.get("data", {}).get("children", [])
        for ch in children:
            if isinstance(ch, dict) and ch.get("kind") == "t3" and isinstance(ch.get("data"), dict):
                posts.append(ch["data"])

        after = data.get("data", {}).get("after")
        if not after:
            break
        sleep_jitter()

    bundle = {
        "fetch_config": cfg,
        "listing_method_used": "A" if str(cfg.get("method", "B")).upper() == "A" else "B",
        "posts": posts,
    }
    listings_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[4/4] done.")
    return {
        "status": "success",
        "listings_path": str(listings_path),
        "posts_count": len(posts),
        "method": method,
    }
