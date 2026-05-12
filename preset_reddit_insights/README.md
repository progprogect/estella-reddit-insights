# Preset: Reddit Insights → Excel (local)

Extella preset: from **explicit master-concept invocation** to an **Excel** workbook of Reddit posts and optional comments.

## Contents

| Path | Purpose |
|------|---------|
| [concepts/master_reddit_insights.md](concepts/master_reddit_insights.md) | Master concept (entry by title) — **English** |
| [concepts/method_*.md](concepts/) | Method **A** / **B** / **C** setup — **English** |
| [concepts/excel_output_contract.md](concepts/excel_output_contract.md) | Excel columns contract — **English** |
| [concepts/rate_limit_policy.md](concepts/rate_limit_policy.md) | Limits and 429 — **English** |
| [concepts/reddit_json_spike_results.md](concepts/reddit_json_spike_results.md) | Spike takeaways — **English** |
| [experts/*.py](experts/) | Expert sources (`fython`; `$extens` — valid only under Extella) |
| [spike/spike_reddit_json.py](spike/spike_reddit_json.py) | Repeatable local HTTP spike |
| [SPIKE_RESULTS.md](SPIKE_RESULTS.md) | Last spike artifact |
| [scripts/bootstrap_api.py](scripts/bootstrap_api.py) | Upload concepts + experts to Extella |
| [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) | Agent system-prompt fragment |

## Master concept: how to invoke

The user must use the **exact** title (first line of the concept body):

**`Reddit Insights → Excel (master)`**

Example: **Run `Reddit Insights → Excel (master)`**

## Local execution and `target`

- **Do not** ask users to copy a preset “default” device UUID from this README.
- For filesystem output, use **Extella’s per-user local execution** so the platform resolves the correct **target** for the signed-in user’s bound device.
- Install **Extella Desktop** and stay signed in when local disk access is required.

## `reddit_app_user_agent`

- It is **not** “found” inside Reddit’s website settings — it is a **string you define** (see master concept and [Reddit API wiki](https://github.com/reddit-archive/reddit/wiki/API)).
- The agent should **propose a draft** if the user is unsure, then save the approved value to KV as `reddit_app_user_agent`.

## KV keys (recommended names)

| Key | Use |
|-----|-----|
| `reddit_client_id` | Method **A** (OAuth) |
| `reddit_client_secret` | Method **A** |
| `reddit_app_user_agent` | Methods **A**, **B**, **C** |

## Publish to Extella

`bootstrap_api.py` reads **`.env`** at the **repository root** (if present): `EXTELLA_API_TOKEN`, `EXTELLA_PROFILE_ID`, `EXTELLA_AGENT_ID`. Existing shell variables take precedence. Copy [`.env.example`](../.env.example) to `.env` and fill the token — **`.env` is gitignored.**

`bootstrap_api.py` also sends **`X-Profile-Id: default`** and **`X-Agent-Id: agent_extella_default`** unless overridden by env.

```bash
cd preset_reddit_insights/scripts
python3 bootstrap_api.py --dry-run
python3 bootstrap_api.py
```

Each `concept/add` creates a **new** row; dedupe or use `concept/update` in the UI if you re-upload often.

## Methods

- **A:** OAuth `client_credentials`, `oauth.reddit.com` listings.
- **B:** Public `.json` on `www.reddit.com`.
- **C:** Same listings as **B**; comments via `old.reddit.com` (or `B` for comments via `comments_engine`).

## Spike

```bash
cd preset_reddit_insights/spike
python3 spike_reddit_json.py
```

Refreshes [SPIKE_RESULTS.md](SPIKE_RESULTS.md).

## Links

- [Roundproxies — How to Scrape Reddit](https://roundproxies.com/blog/reddit/)
- [Simon Willison — Reddit JSON](https://til.simonwillison.net/reddit/scraping-reddit-json)
