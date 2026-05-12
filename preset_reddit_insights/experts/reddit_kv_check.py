$extens("include.py")
include("import json", [])


def reddit_kv_check(
    method: str = "B",
    reddit_client_id: str = "",
    reddit_client_secret: str = "",
    app_user_agent: str = "",
) -> dict:
    """Validates required parameters for the selected Reddit access method before fetch."""
    m = (method or "").strip().upper()
    if m not in ("A", "B", "C"):
        return {"status": "error", "message": "method must be one of A, B, C"}

    missing = []
    if m == "A":
        if not reddit_client_id:
            missing.append("reddit_client_id")
        if not reddit_client_secret:
            missing.append("reddit_client_secret")

    if not app_user_agent:
        missing.append("app_user_agent (set from KV reddit_app_user_agent or user input)")

    if missing:
        return {
            "status": "error",
            "message": "Missing values for method " + m + ": " + ", ".join(missing),
            "missing": missing,
        }

    return {"status": "success", "method": m, "checked": True}
