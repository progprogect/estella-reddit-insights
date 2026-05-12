#!/usr/bin/env python3
"""
Upload preset concepts + experts to Extella via REST API.

Requires:
  export EXTELLA_API_TOKEN="..."   # or EXTELLA_TOKEN (same value as in Extella CLI docs)

Optional (defaults match Extella platform conventions):
  export EXTELLA_PROFILE_ID="default"          # X-Profile-Id (default: default)
  export EXTELLA_AGENT_ID="agent_extella_default"  # X-Agent-Id (default: agent_extella_default)
  export EXTELLA_BASE_URL="https://api.extella.ai"

Usage:
  python3 bootstrap_api.py              # upload all
  python3 bootstrap_api.py --dry-run    # print actions only
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
EXPERTS_DIR = ROOT / "experts"

BASE_URL = os.environ.get("EXTELLA_BASE_URL", "https://api.extella.ai").rstrip("/")
TOKEN = os.environ.get("EXTELLA_API_TOKEN") or os.environ.get("EXTELLA_TOKEN") or ""
PROFILE_ID = (os.environ.get("EXTELLA_PROFILE_ID") or "default").strip()
AGENT_ID = (os.environ.get("EXTELLA_AGENT_ID") or "agent_extella_default").strip()


EXPERTS: list[dict] = [
    {
        "name": "reddit_kv_check",
        "description": (
            "Validates required parameters for Reddit preset by method. "
            "Parameters: method — A|B|C; reddit_client_id, reddit_client_secret — required for A; "
            "app_user_agent — required (KV reddit_app_user_agent or user-approved draft; agent may propose a UA string per Reddit rules)."
        ),
        "kwargs": {
            "method": "B",
            "reddit_client_id": "",
            "reddit_client_secret": "",
            "app_user_agent": "",
        },
        "cspl": "fython",
        "file": "reddit_kv_check.py",
    },
    {
        "name": "reddit_discover",
        "description": (
            "Builds fetch_config for Reddit listings. Parameters: method A|B|C; mode search|subreddit_hot|subreddit_new; "
            "query; subreddit without r/; sort; time_filter; max_pages; limit_per_page; min_delay_sec; max_delay_sec; "
            "fetch_comments bool; max_posts_for_comments; comment_limit; comments_engine B|C; app_user_agent."
        ),
        "kwargs": {
            "method": "B",
            "mode": "search",
            "query": "",
            "subreddit": "",
            "sort": "new",
            "time_filter": "week",
            "max_pages": 5,
            "limit_per_page": 100,
            "min_delay_sec": 2.0,
            "max_delay_sec": 4.0,
            "fetch_comments": False,
            "max_posts_for_comments": 10,
            "comment_limit": 100,
            "comments_engine": "C",
            "app_user_agent": "",
        },
        "cspl": "fython",
        "file": "reddit_discover.py",
    },
    {
        "name": "reddit_fetch_pages",
        "description": (
            "Fetches Reddit listing JSON (method A OAuth or B public). "
            "Parameters: fetch_config_json — output of reddit_discover; output_dir — expanded path; "
            "reddit_client_id, reddit_client_secret for method A; app_user_agent required."
        ),
        "kwargs": {
            "fetch_config_json": "",
            "output_dir": "",
            "reddit_client_id": "",
            "reddit_client_secret": "",
            "app_user_agent": "",
        },
        "cspl": "fython",
        "file": "reddit_fetch_pages.py",
    },
    {
        "name": "reddit_fetch_comments",
        "description": (
            "Fetches comment threads for posts from listings JSON. "
            "Parameters: listings_path; output_dir; app_user_agent; comments_engine B|C; "
            "max_posts_for_comments; comment_limit; min_delay_sec; max_delay_sec."
        ),
        "kwargs": {
            "listings_path": "",
            "output_dir": "",
            "app_user_agent": "",
            "comments_engine": "C",
            "max_posts_for_comments": 10,
            "comment_limit": 100,
            "min_delay_sec": 2.0,
            "max_delay_sec": 4.0,
        },
        "cspl": "fython",
        "file": "reddit_fetch_comments.py",
    },
    {
        "name": "reddit_normalize_records",
        "description": (
            "Normalizes listings (+ optional comments file) to flat records JSON. "
            "Parameters: listings_path; comments_path optional; output_dir; comments_engine B|C."
        ),
        "kwargs": {
            "listings_path": "",
            "comments_path": "",
            "output_dir": "",
            "comments_engine": "C",
        },
        "cspl": "fython",
        "file": "reddit_normalize_records.py",
    },
    {
        "name": "reddit_export_xlsx",
        "description": (
            "Exports normalized records to Excel with sheets posts and comments. "
            "Parameters: records_path; output_dir; workbook_name without extension."
        ),
        "kwargs": {
            "records_path": "",
            "output_dir": "",
            "workbook_name": "reddit_insights",
        },
        "cspl": "fython",
        "file": "reddit_export_xlsx.py",
    },
]

CONCEPT_FILES = [
    "master_reddit_insights.md",
    "method_a_oauth_setup.md",
    "method_b_json_setup.md",
    "method_c_oldreddit_setup.md",
    "excel_output_contract.md",
    "rate_limit_policy.md",
    "reddit_json_spike_results.md",
]


def post_json(path: str, payload: dict, dry: bool) -> dict:
    if dry:
        print(f"DRY {path} keys={list(payload.keys())}")
        return {"status": "dry_run"}
    headers = {
        "X-Auth-Token": TOKEN,
        "Content-Type": "application/json",
        "X-Profile-Id": PROFILE_ID,
        "X-Agent-Id": AGENT_ID,
    }
    r = requests.post(
        BASE_URL + path,
        headers=headers,
        json=payload,
        timeout=120,
    )
    try:
        data = r.json()
    except Exception:
        data = {"_text": r.text[:500]}
    if r.status_code >= 400:
        raise RuntimeError(f"{path} HTTP {r.status_code}: {data}")
    return data


def upload_concepts(dry: bool) -> None:
    for name in CONCEPT_FILES:
        p = CONCEPTS_DIR / name
        if not p.exists():
            print(f"skip missing concept file: {p}", file=sys.stderr)
            continue
        text = p.read_text(encoding="utf-8")
        print(f"concept/add {name} ({len(text)} chars)")
        resp = post_json("/api/concept/add", {"text": text}, dry)
        if not dry and isinstance(resp, dict):
            print(f"  -> response: id={resp.get('id')} status={resp.get('status')}")


def upload_experts(dry: bool) -> None:
    for spec in EXPERTS:
        fp = EXPERTS_DIR / spec["file"]
        code = fp.read_text(encoding="utf-8")
        payload = {
            "name": spec["name"],
            "description": spec["description"],
            "code": code,
            "kwargs": spec["kwargs"],
            "cspl": spec["cspl"],
        }
        print(f"expert/save {spec['name']}")
        resp = post_json("/api/expert/save", payload, dry)
        if not dry and isinstance(resp, dict):
            print(f"  -> response: status={resp.get('status')} expert_name={resp.get('expert_name')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = bool(args.dry_run)

    if not dry and not TOKEN:
        print("Set EXTELLA_API_TOKEN or EXTELLA_TOKEN", file=sys.stderr)
        sys.exit(1)

    upload_concepts(dry)
    upload_experts(dry)
    print("Done.")


if __name__ == "__main__":
    main()
