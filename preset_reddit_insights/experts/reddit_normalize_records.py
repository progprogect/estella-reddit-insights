$extens("include.py")
include("import json", [])
include("from datetime import datetime, timezone", [])
include("from pathlib import Path", [])
include("from typing import Optional, Union", [])


def reddit_normalize_records(
    listings_path: str = "",
    comments_path: str = "",
    output_dir: str = "",
    comments_engine: str = "C",
) -> dict:
    """Flattens listings + optional comment threads into normalized JSON for Excel export."""

    def _full_permalink(permalink: str) -> str:
        p = (permalink or "").strip()
        if not p:
            return ""
        if p.startswith("http"):
            return p
        if p.startswith("/"):
            return "https://www.reddit.com" + p
        return "https://www.reddit.com/" + p

    def _utc_iso(ts: Optional[Union[float, int]]) -> str:
        if ts is None:
            return ""
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
        except Exception:
            return ""

    def _walk_replies(replies_obj, depth: int, post_subreddit: str, source_method: str, post_permalink: str):
        if not replies_obj or isinstance(replies_obj, str):
            return
        if not isinstance(replies_obj, dict):
            return
        children = replies_obj.get("data", {}).get("children", [])
        for ch in children:
            if not isinstance(ch, dict):
                continue
            if ch.get("kind") != "t1":
                continue
            d = ch.get("data") or {}
            rid = d.get("id", "")
            rec = {
                "record_id": ("t1_" + rid) if rid else "",
                "kind": "comment",
                "subreddit": d.get("subreddit") or post_subreddit,
                "title": "",
                "body": (d.get("body") or "")[:50000],
                "permalink": _full_permalink(d.get("permalink", "")),
                "url": "",
                "author": d.get("author", ""),
                "created_utc": _utc_iso(d.get("created_utc")),
                "score": d.get("score", ""),
                "num_comments": "",
                "parent_id": d.get("parent_id", ""),
                "parent_permalink": post_permalink,
                "depth": depth,
                "source_method": source_method,
            }
            yield rec
            for sub in _walk_replies(d.get("replies"), depth + 1, post_subreddit, source_method, post_permalink):
                yield sub

    print("[1/3] reddit_normalize_records: validate...")
    if not listings_path:
        return {"status": "error", "message": "listings_path is required"}
    if not output_dir:
        return {"status": "error", "message": "output_dir is required"}

    lp = Path(listings_path).expanduser().resolve()
    if not lp.exists():
        return {"status": "error", "message": f"listings not found: {lp}"}

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path = out_dir / "reddit_records_normalized.json"

    bundle = json.loads(lp.read_text(encoding="utf-8"))
    cfg = bundle.get("fetch_config", {}) or {}
    listing_method_used = bundle.get("listing_method_used")
    if not listing_method_used:
        m0 = str(cfg.get("method", "B")).upper()
        listing_method_used = "A" if m0 == "A" else "B"
    posts = bundle.get("posts", []) or []

    records: list[dict] = []

    for p in posts:
        if not isinstance(p, dict):
            continue
        pid = p.get("id", "")
        rec = {
            "record_id": ("t3_" + pid) if pid else "",
            "kind": "post",
            "subreddit": p.get("subreddit", ""),
            "title": (p.get("title") or "")[:10000],
            "body": (p.get("selftext") or "")[:50000],
            "permalink": _full_permalink(p.get("permalink", "")),
            "url": p.get("url", "") or "",
            "author": p.get("author", ""),
            "created_utc": _utc_iso(p.get("created_utc")),
            "score": p.get("score", ""),
            "num_comments": p.get("num_comments", ""),
            "parent_id": "",
            "parent_permalink": "",
            "depth": "",
            "source_method": listing_method_used,
        }
        records.append(rec)

    cp = (comments_path or "").strip()
    if cp:
        cpp = Path(cp).expanduser().resolve()
        if cpp.exists():
            print("[2/3] merging comments...")
            eng = (comments_engine or str(cfg.get("comments_engine", "C"))).strip().upper()
            cdata = json.loads(cpp.read_text(encoding="utf-8"))
            for th in cdata.get("threads", []) or []:
                payload = th.get("json")
                if not isinstance(payload, list) or len(payload) < 2:
                    continue
                post_listing = payload[0]
                comment_listing = payload[1]
                post_children = (post_listing or {}).get("data", {}).get("children", [])
                post_data = {}
                if post_children and isinstance(post_children[0], dict):
                    if post_children[0].get("kind") == "t3":
                        post_data = post_children[0].get("data") or {}
                sub = post_data.get("subreddit", "")
                post_permalink = _full_permalink(post_data.get("permalink", ""))

                children = (comment_listing or {}).get("data", {}).get("children", [])
                for ch in children:
                    if not isinstance(ch, dict) or ch.get("kind") != "t1":
                        continue
                    d = ch.get("data") or {}
                    rid = d.get("id", "")
                    rec = {
                        "record_id": ("t1_" + rid) if rid else "",
                        "kind": "comment",
                        "subreddit": d.get("subreddit") or sub,
                        "title": "",
                        "body": (d.get("body") or "")[:50000],
                        "permalink": _full_permalink(d.get("permalink", "")),
                        "url": "",
                        "author": d.get("author", ""),
                        "created_utc": _utc_iso(d.get("created_utc")),
                        "score": d.get("score", ""),
                        "num_comments": "",
                        "parent_id": d.get("parent_id", ""),
                        "parent_permalink": post_permalink,
                        "depth": 0,
                        "source_method": eng if eng in ("B", "C") else "C",
                    }
                    records.append(rec)
                    for subrec in _walk_replies(d.get("replies"), 1, sub, eng if eng in ("B", "C") else "C", post_permalink):
                        records.append(subrec)

    records_path.write_text(json.dumps({"records": records}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[3/3] done.")
    return {"status": "success", "records_path": str(records_path), "records_count": len(records)}
