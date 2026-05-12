# RateLimit_Policy — network and resilience

## User-Agent
- Always send a **meaningful** `User-Agent` (not a library default string).
- Pattern: `AppName/semver (purpose; contact: ...)`
- KV key: `reddit_app_user_agent` — if the user is unsure, **generate a draft** for them (see master concept), confirm, then store in KV.

## Speed
- Between Reddit HTTP calls: **2.0–4.0 s** random jitter unless the user overrides.
- Do **not** default to parallel fan-out to Reddit (429 risk).

## 429 Too Many Requests
1. Read `Retry-After` (seconds) and wait.
2. If missing — sleep **60 s**, retry up to **3** times for that URL.
3. If still failing — return `status=error` with message and **partial** data if files already exist.

## Volume defaults
- Listing `max_pages`: **5**
- Posts to expand for comments: **10** (`max_posts_for_comments`, configurable)
- `comment_limit` in old.reddit URL: **100** (ceiling ~**500**)

## References
- Public `.json` and old.reddit patterns are described in open guides (e.g. [Roundproxies — How to Scrape Reddit](https://roundproxies.com/blog/reddit/)); Reddit may change behavior over time.
