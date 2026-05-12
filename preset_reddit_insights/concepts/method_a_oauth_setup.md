# Method_A_OAuth_Setup — official Reddit API (read)

## When to use
Method **A**: OAuth **`client_credentials`** (application-only, no end-user Reddit login) to read public data via `oauth.reddit.com`. Useful for reporting and more predictable limits than ad-hoc scraping.

## What to prepare
1. Reddit: **Create App** (often **script** or **web app**; use the app’s `client_id` and `client_secret`).
2. In Extella **KV Store** save:
   - `reddit_client_id`
   - `reddit_client_secret`
3. (Recommended) KV key `reddit_app_user_agent` — see the master concept section **`reddit_app_user_agent`**: compose or offer a generated draft, then store in KV.

## What the preset does
Expert `reddit_fetch_pages` for **A** obtains an access token (`POST /api/v1/access_token`), then calls `oauth.reddit.com` according to parameters from `reddit_discover`.

## Limits
- Valid Reddit app credentials required; quotas follow Reddit policy.
- Never put secrets in concepts — only the KV key names above.

## Before run
Call expert `reddit_kv_check` with `method="A"` — it checks required fields are non-empty (the agent injects KV values into run params).

## Execution target
For Excel on disk, rely on **Extella’s per-user resolved local execution target**. Do not instruct users to paste a fixed default device UUID from documentation.
