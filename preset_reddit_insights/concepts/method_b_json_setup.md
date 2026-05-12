# Method_B_JSON_Setup — public `.json` endpoints

## When to use
Method **B**: HTTP GET to Reddit’s public JSON pages (`search.json`, `/r/{sub}/hot.json`, etc.) **without OAuth**.

## Pros / cons (user-facing)
- **Pros:** Minimal setup; structured JSON.
- **Cons:** Strict IP / `User-Agent` limits; possible **429**; unofficial contract may change.

## What to prepare
1. KV key `reddit_app_user_agent` — see master concept **`reddit_app_user_agent`**: explain it is user-defined (not “found” in Reddit UI), offer a **generated draft** if the user is stuck, confirm, then save to KV.
2. For Excel and intermediate JSON files on the user’s machine: run experts via **Extella’s per-user local execution** so the platform applies the correct **target** automatically. **Do not** document a single shared default device UUID for all users.

## Preset behavior
- `reddit_discover` builds config (`mode`: `search` | `subreddit_hot` | `subreddit_new`).
- `reddit_fetch_pages` uses **jitter**, `after` pagination, and **429** handling (see `RateLimit_Policy`).

## Defaults
See `Reddit_JSON_Spike_Results` and the master concept: `max_pages=5`, **2–4 s** jitter between pages.

## Execution target
Same as all methods: **Extella resolves the user’s execution target** for local filesystem output — no preset-wide hardcoded device id.
