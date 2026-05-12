# Reddit_JSON_Spike_Results — environment check

Source: local script `preset_reddit_insights/spike/spike_reddit_json.py`, artifact `SPIKE_RESULTS.md`.

## Findings (short)
- `search.json` and `r/{sub}/hot.json` returned **HTTP 200** with a proper `User-Agent`.
- Pagination with `after` for 2 pages — **200** for both.
- `old.reddit.com/comments/{id}.json` — response had **two** listings; top-level comments present.

## Recommended preset defaults
Also see the master concept:
- Jitter **2.0–4.0 s** between pages.
- `max_pages = 5`.
- Default `comment_limit` **100** (ceiling ~**500**).
- **429**: `Retry-After` or 60 s backoff, up to 3 attempts.
