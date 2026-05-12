# Reddit Insights → Excel (master)

## Purpose
This preset guides the user from an **explicit start** to an **Excel workbook** of Reddit mentions: posts and (optionally) comments, links, and basic author fields available from public Reddit data.

## Mandatory entry point
The user must **explicitly invoke this master concept by its exact title** in the first intentional message, for example:
**Run `Reddit Insights → Excel (master)`** — the title must match the concept record in Extella.

Until then, the agent **must not** start collection and **must not** ask for keywords.

## Dialogue state machine
0. **Awaiting entry:** If the user has not named the master concept, politely ask them to use the phrase from **Mandatory entry point**.
1. **Choose method A / B / C** — show the table (see method sub-concepts). Short pros/cons. Wait for an explicit letter.
2. **Method onboarding:** Open the matching sub-concept (`Method_A_OAuth_Setup`, `Method_B_JSON_Setup`, `Method_C_OldReddit_Setup`) and walk through steps (KV for Reddit app on **A**; `reddit_app_user_agent` for all; `output_dir` for Excel paths).
3. **Collect topic:** keywords or topic; optional subreddit(s); sort; time window; `max_pages`; whether to fetch comments and limits on posts/comments.
4. **Confirm:** Short recap; ask for approval (e.g. “OK”).
5. **Run experts (local filesystem output):** Run the chain below. **Do not** ask the user for a device UUID or document a shared “default target”. Extella resolves the **per-user execution target** (the user’s bound local runtime / device) when experts need to write files to disk — use the same local execution path the product uses for that user. Then call, in order:
   - `reddit_kv_check` (for **all** methods: **A** — OAuth keys; **B/C** — including non-empty `app_user_agent`),
   - `reddit_discover` → `reddit_fetch_pages` → `reddit_fetch_comments` (if enabled) → `reddit_normalize_records` → `reddit_export_xlsx`.

## Method matrix (short)
| Method | What it is | When |
|--------|------------|------|
| **A** | Official OAuth (`client_credentials` for public read) via `oauth.reddit.com` | You want stability and predictable limits |
| **B** | Public `.json` listings (`search.json`, subreddit listings) without OAuth | Fast start, no Reddit app setup |
| **C** | Same listings as **B**; comment trees via **old.reddit** (`comments_engine=C` by default) | You need discussion threads without OAuth |

Details live only in the method sub-concepts.

## Special case
If the first message names the master concept **and** already includes keywords: still complete steps **1–2** (method + onboarding), **then** accept or refine the topic wording.

## Legal / ethical
Only **public** posts/comments; moderate volume; respect rate limits and `User-Agent`; do not encourage ToS violations or moderation bypass.

## Related concepts
- `Method_A_OAuth_Setup`
- `Method_B_JSON_Setup`
- `Method_C_OldReddit_Setup`
- `Excel_Output_Contract`
- `RateLimit_Policy`
- `Reddit_JSON_Spike_Results` (empirical defaults after spike)

## KV keys (names only — never values in concepts)
- `reddit_client_id`, `reddit_client_secret` — for method **A** (values only in KV).
- `reddit_app_user_agent` — **recommended for A, B, and C** (see below).

## `reddit_app_user_agent` — what it is and how to help the user
- Reddit expects a **unique, descriptive `User-Agent`** for HTTP access. It is **not** copied from a “Reddit settings” page — the author **defines** a stable string (see [Reddit API rules](https://github.com/reddit-archive/reddit/wiki/API) for the usual shape).
- **Good pattern:** `AppName/semver (by /u/RedditUsername; contact: email or URL)`.
- **Where it “comes from”:** The user (or you) composes it from: app label (e.g. `EstellaRedditInsights`), version (`1.0`), their Reddit username if they have one (`by /u/...`), and optional contact.
- **Agent behavior:** If the user does not know what to put, **generate a draft** for them, e.g. `EstellaRedditInsights/1.0 (by /u/<their_username>; contact: <ask once>)`, let them edit/confirm, then save to KV as `reddit_app_user_agent`.

## Default limits (from spike)
- Jitter between pages: **2.0–4.0 s**.
- Default `max_pages`: **5**.
- Default `comment_limit` per post (old.reddit): **100**, practical ceiling **500** (user’s risk if higher).
- On **429**: honor `Retry-After`, else backoff **60 s**, up to **3** retries.
