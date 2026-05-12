# Excel_Output_Contract — export format

## File
- Extension: `.xlsx`
- Path: `{output_dir}/{workbook_name}.xlsx` (directory with `expanduser`, e.g. `~/Downloads/EstellaReddit`)
- Sheets:
  - `posts` — listing posts found
  - `comments` — comments if `reddit_fetch_comments` ran; otherwise empty sheet with headers

## Columns (minimum)
Implemented in `reddit_export_xlsx`:
- `record_id` — stable id (`t3_` / `t1_` or Reddit id)
- `kind` — `post` | `comment`
- `subreddit`
- `title` — post only; empty for comments
- `body` — selftext or comment body (truncation policy can be extended later)
- `permalink` — full URL `https://www.reddit.com...`
- `url` — post link (posts)
- `author`
- `created_utc` — ISO UTC
- `score`
- `num_comments` — posts
- `parent_id` / `parent_permalink` — comments when available
- `depth` — tree depth (0 = top-level)
- `source_method` — `A` | `B` | `C`

## Local execution
Run export on the user’s machine via **Extella’s resolved local execution context** so `pandas` / `openpyxl` can write to the user’s filesystem. **Do not** assume or document one global default device UUID; the platform assigns the correct per-user **target** when running locally.
