# Reddit JSON spike results
Generated (UTC): 2026-05-12T13:55:17.353411+00:00
User-Agent: `EstellaRedditInsightsSpike/0.1 (research; contact: local-spike)`
## B1: www.reddit.com/search.json
- HTTP: **200** (765 ms)
- children count: **10**
- first post `id` (fullname prefix t3_): **1tb0knt**

## B2: Pagination `after` (search.json, 2 pages)
- page 1: HTTP **200**
- got **10** rows, `after`=set
- page 2: HTTP **200**
- got **10** rows, `after`=set
- total rows collected: **20**

## B3: r/python/hot.json (limit=5)
- HTTP: **200**
- first hot post id: **1t8r5sf**

## C: old.reddit.com/comments/{id}.json?limit=50
- URL: `https://old.reddit.com/comments/1t8r5sf.json`
- HTTP: **200**
- listings in response: **2** (expected 2)
- top-level comment nodes: **9**

## Recommended preset defaults (from spike heuristics)
- Sequential requests with **2.0–4.0 s** jitter between pages.
- Default **max_pages**: **5** for search/listing (adjust after prod tests).
- Default **comment_limit** per post for old.reddit: **100** (cap; user can raise to 500).
- Always set descriptive **User-Agent** (app name + purpose); never use library default.
- On **429**: honor **Retry-After** if present; else backoff **60 s** and retry up to **3** times.
