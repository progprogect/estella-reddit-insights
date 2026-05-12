$extens("include.py")
include("import json", [])
include("import openpyxl", ["extella-pip install openpyxl"])
include("import pandas as pd", ["extella-pip install pandas"])
include("from pathlib import Path", [])


def reddit_export_xlsx(
    records_path: str = "",
    output_dir: str = "",
    workbook_name: str = "reddit_insights",
) -> dict:
    """Writes posts and comments sheets from normalized records JSON."""
    print("[1/2] reddit_export_xlsx: validate...")
    if not records_path:
        return {"status": "error", "message": "records_path is required"}
    if not output_dir:
        return {"status": "error", "message": "output_dir is required"}

    rp = Path(records_path).expanduser().resolve()
    if not rp.exists():
        return {"status": "error", "message": f"records file not found: {rp}"}

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(rp.read_text(encoding="utf-8"))
    rows = data.get("records", [])
    if not isinstance(rows, list):
        return {"status": "error", "message": "invalid records JSON"}

    posts = [r for r in rows if isinstance(r, dict) and r.get("kind") == "post"]
    comments = [r for r in rows if isinstance(r, dict) and r.get("kind") == "comment"]

    cols = [
        "record_id",
        "kind",
        "subreddit",
        "title",
        "body",
        "permalink",
        "url",
        "author",
        "created_utc",
        "score",
        "num_comments",
        "parent_id",
        "parent_permalink",
        "depth",
        "source_method",
    ]

    df_posts = pd.DataFrame.from_records(posts, columns=cols) if posts else pd.DataFrame(columns=cols)
    df_comments = pd.DataFrame.from_records(comments, columns=cols) if comments else pd.DataFrame(columns=cols)

    safe_name = "".join(ch for ch in (workbook_name or "reddit_insights") if ch.isalnum() or ch in ("-", "_"))[:80]
    if not safe_name:
        safe_name = "reddit_insights"

    xlsx_path = out_dir / f"{safe_name}.xlsx"
    print("[2/2] writing workbook...")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_posts.to_excel(writer, index=False, sheet_name="posts")
        df_comments.to_excel(writer, index=False, sheet_name="comments")

    return {
        "status": "success",
        "xlsx_path": str(xlsx_path),
        "posts_rows": len(df_posts),
        "comments_rows": len(df_comments),
    }
