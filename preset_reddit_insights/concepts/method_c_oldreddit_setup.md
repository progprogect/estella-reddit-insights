# Method_C_OldReddit_Setup — comments via old.reddit

## When to use
Method **C**: load comment trees from `https://old.reddit.com/comments/{post_id}.json?limit=...` (no browser).

## Typical combination
Usually **B → find posts → C → fetch comments** for a capped number of posts (`max_posts_for_comments`).

## Pros / cons
- **Pros:** Up to **500** comments per request at the top listing (nested replies in `replies`); no JS.
- **Cons:** Unofficial path; Reddit may change behavior; deep trees need `replies` walking.

## What to prepare
Use the same descriptive **`User-Agent`** as for **B** — KV `reddit_app_user_agent` (see master concept: compose or **generate a draft** for the user, then KV).

## Preset behavior
Expert `reddit_fetch_comments` reads the listings file from `reddit_fetch_pages`, extracts `post_id`, fetches old.reddit JSON per post (up to the cap), and writes raw JSON for normalization.

## Execution target
Same as methods **A** and **B**: rely on **Extella’s per-user resolved local target** for file output — no shared default device UUID in docs.
