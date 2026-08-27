"""
corpus/reclassify_unavailable.py — mark permanently-gone clone_failed repos.

Some candidates are deleted or made private on GitHub between candidate
discovery and cloning. They return HTTP 404 from the REST API, git clone
fails with an auth prompt, and no amount of retrying can succeed. This
script reclassifies those entries in exclusion_log.json from the transient
`clone_failed` to the permanent `unavailable`, documenting population
attrition and keeping retry rounds bounded to repos that still exist.

Usage:
    python corpus/reclassify_unavailable.py            # dry run
    python corpus/reclassify_unavailable.py --apply    # write changes

Requires GITHUB_TOKEN (from .env) for API status checks.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / ".env")

GITHUB_API = "https://api.github.com"


def gh_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN env var is required")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def repo_status(full_name: str, headers: dict) -> tuple[str, int | str]:
    try:
        r = requests.get(f"{GITHUB_API}/repos/{full_name}", headers=headers, timeout=15)
        return full_name, r.status_code
    except requests.RequestException as exc:
        return full_name, f"error: {exc}"


def main():
    ap = argparse.ArgumentParser(description="Reclassify dead clone_failed repos as unavailable")
    ap.add_argument("--apply", action="store_true", help="Write changes to exclusion_log.json")
    ap.add_argument(
        "--recheck", action="store_true",
        help="Re-check ALL unavailable entries too (a repo that came back is set back to clone_failed)",
    )
    args = ap.parse_args()

    path = ROOT / "exclusion_log.json"
    data = json.loads(path.read_text())

    cf = [e for e in data["excluded"] if e["reason"] == "clone_failed"]
    names = sorted({e["full_name"] for e in cf})
    if args.recheck:
        names += sorted({e["full_name"] for e in data["excluded"] if e["reason"] == "unavailable"})
    names = sorted(set(names))
    print(f"[reclassify] checking {len(names)} repos against the GitHub API")

    headers = gh_headers()
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with ThreadPoolExecutor(16) as pool:
        results = dict(pool.map(lambda n: repo_status(n, headers), names))

    gone = {n for n, s in results.items() if s == 404}
    alive = {n for n, s in results.items() if s == 200}
    other = {n: s for n, s in results.items() if s not in (200, 404)}

    flipped_out, flipped_in = 0, 0
    for e in data["excluded"]:
        n = e["full_name"]
        if e["reason"] == "clone_failed" and n in gone:
            e["reason"] = "unavailable"
            e["detail"] = f"GitHub API 404 at {checked_at} (deleted or private)"
            flipped_out += 1
        elif args.recheck and e["reason"] == "unavailable" and n in alive:
            e["reason"] = "clone_failed"
            e.pop("detail", None)
            flipped_in += 1

    print(
        f"[reclassify] 404 (gone): {len(gone)} | 200 (alive): {len(alive)} | "
        f"other (untouched): {len(other)}"
    )
    for n, s in sorted(other.items()):
        print(f"  ? {n}: {s}")
    print(
        f"[reclassify] clone_failed -> unavailable: {flipped_out}"
        + (f" | unavailable -> clone_failed (revived): {flipped_in}" if args.recheck else "")
    )

    counts: dict[str, int] = {}
    for e in data["excluded"]:
        counts[e["reason"]] = counts.get(e["reason"], 0) + 1
    print("[reclassify] exclusion reasons after:", dict(sorted(counts.items())))

    if args.apply:
        data["generated_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(data, indent=2))
        print(f"[reclassify] wrote {path}")
    else:
        print("[reclassify] dry run; use --apply to persist")


if __name__ == "__main__":
    main()
