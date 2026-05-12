#!/usr/bin/env python3
"""
Spike: verify Reddit public JSON + old.reddit comment JSON from this environment.
Writes ../SPIKE_RESULTS.md — do not commit secrets; this script uses no credentials.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

UA = "EstellaRedditInsightsSpike/0.1 (research; contact: local-spike)"
TIMEOUT = 30


def log_line(msg: str) -> str:
    return msg


def fetch_json(session: requests.Session, url: str, params: dict | None = None) -> tuple[int, dict | list | str]:
    r = session.get(url, params=params or {}, timeout=TIMEOUT)
    text = r.text[:2000] if r.text else ""
    try:
        data = r.json()
    except Exception:
        data = {"_non_json_preview": text}
    return r.status_code, data


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    lines: list[str] = []
    lines.append(f"# Reddit JSON spike results\n")
    lines.append(f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"User-Agent: `{UA}`\n")

    # --- B1: search.json ---
    url_search = "https://www.reddit.com/search.json"
    params_search = {"q": "python asyncio", "limit": 10, "sort": "new", "type": "link"}
    t0 = time.perf_counter()
    code, data = fetch_json(session, url_search, params_search)
    dt_ms = (time.perf_counter() - t0) * 1000
    lines.append("## B1: www.reddit.com/search.json\n")
    lines.append(f"- HTTP: **{code}** ({dt_ms:.0f} ms)\n")
    if isinstance(data, dict) and "data" in data:
        children = data.get("data", {}).get("children", [])
        lines.append(f"- children count: **{len(children)}**\n")
        first_id = None
        if children and isinstance(children[0], dict):
            first_id = children[0].get("data", {}).get("id")
        lines.append(f"- first post `id` (fullname prefix t3_): **{first_id}**\n")
    else:
        lines.append(f"- unexpected shape keys: `{list(data)[:20] if isinstance(data, dict) else type(data)}`\n")

    # --- B2: pagination after ---
    lines.append("\n## B2: Pagination `after` (search.json, 2 pages)\n")
    after = None
    total = 0
    for page in range(2):
        p = dict(params_search)
        if after:
            p["after"] = after
        code2, data2 = fetch_json(session, url_search, p)
        lines.append(f"- page {page + 1}: HTTP **{code2}**\n")
        if code2 == 429:
            ra = session.get(url_search, params=p, timeout=TIMEOUT).headers.get("Retry-After")
            lines.append(f"- Retry-After header: `{ra}`\n")
            break
        if not isinstance(data2, dict) or "data" not in data2:
            lines.append("- stop: non-listing response\n")
            break
        ch = data2["data"].get("children", [])
        total += len(ch)
        after = data2["data"].get("after")
        lines.append(f"- got **{len(ch)}** rows, `after`={'set' if after else 'null'}\n")
        time.sleep(2.2)
    lines.append(f"- total rows collected: **{total}**\n")

    # --- B3: subreddit hot.json ---
    lines.append("\n## B3: r/python/hot.json (limit=5)\n")
    code3, data3 = fetch_json(session, "https://www.reddit.com/r/python/hot.json", {"limit": 5})
    lines.append(f"- HTTP: **{code3}**\n")
    post_id = None
    if isinstance(data3, dict) and "data" in data3:
        ch3 = data3["data"].get("children", [])
        if ch3 and isinstance(ch3[0], dict):
            post_id = ch3[0].get("data", {}).get("id")
        lines.append(f"- first hot post id: **{post_id}**\n")

    # --- C: old.reddit comments.json ---
    lines.append("\n## C: old.reddit.com/comments/{id}.json?limit=50\n")
    if not post_id:
        post_id = "1"  # unlikely to work
    url_old = f"https://old.reddit.com/comments/{post_id}.json"
    code4, data4 = fetch_json(session, url_old, {"limit": 50})
    lines.append(f"- URL: `{url_old}`\n")
    lines.append(f"- HTTP: **{code4}**\n")
    if isinstance(data4, list) and len(data4) >= 2:
        comments_root = data4[1].get("data", {}).get("children", [])
        lines.append(f"- listings in response: **{len(data4)}** (expected 2)\n")
        lines.append(f"- top-level comment nodes: **{len(comments_root)}**\n")
    else:
        lines.append(f"- shape: `{type(data4).__name__}`\n")

    # --- Recommended defaults (conservative) ---
    lines.append("\n## Recommended preset defaults (from spike heuristics)\n")
    lines.append("- Sequential requests with **2.0–4.0 s** jitter between pages.\n")
    lines.append("- Default **max_pages**: **5** for search/listing (adjust after prod tests).\n")
    lines.append("- Default **comment_limit** per post for old.reddit: **100** (cap; user can raise to 500).\n")
    lines.append("- Always set descriptive **User-Agent** (app name + purpose); never use library default.\n")
    lines.append("- On **429**: honor **Retry-After** if present; else backoff **60 s** and retry up to **3** times.\n")

    out = Path(__file__).resolve().parent.parent / "SPIKE_RESULTS.md"
    out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
