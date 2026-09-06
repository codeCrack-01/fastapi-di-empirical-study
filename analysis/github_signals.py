"""
analysis/github_signals.py — Phase 2B: maintainer/issue signals per repo.

Pulls, for each accepted repo, GitHub maintainer-health signals (a cross-sectional
snapshot; NOT a longitudinal defect study): open issues, open PRs, contributor
count, last-push recency. Used as outcome/confounder signals in the DI-pattern
comparison.

Requires the same fine-grained read-only GITHUB_TOKEN as the finder (loaded from
corpus/.env). Rate limits ~5k requests/hour for this token type — 402 repos x 2
calls (repo + contributors) ~= 804, so run once and cache to disk. A cache file
(analysis/out/github_signals_raw.json) lets reruns proceed offline.

Output: analysis/out/github_signals.csv
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
ENV_FILE = ROOT.parent / ".env"
MANIFEST = ROOT.parent / "corpus" / "manifest.json"
CACHE = OUT_DIR / "github_signals_raw.json"

API = "https://api.github.com"


def _load_accepted() -> list[str]:
    return [a["full_name"] for a in json.loads(MANIFEST.read_text())["accepted"]]


def _load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {}


def _gh_get(token, url: str, timeout: int = 30):
    """Return (json_body, response_headers) or (None, headers)."""
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json"}
    for attempt in range(4):
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            return r.json(), r.headers
        if r.status_code == 403 and "rate limit" in r.text.lower():
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - time.time(), 1) + 2
            print(f"   rate-limited; sleeping {wait:.0f}s", flush=True)
            time.sleep(wait)
            continue
        if r.status_code in (404,):
            return None, r.headers
        if r.status_code >= 500 or r.status_code in (429,):
            time.sleep(2 ** attempt)
            continue
        return None, r.headers
    return None, {}


def _parse_link(page_link: str) -> int:
    """Extract the final page number from a GitHub Link 'rel=last' header."""
    import re
    m = re.findall(r"page=(\d+)>; rel=\"last\"", page_link)
    return int(m[0]) if m else 0


def main() -> None:
    load_dotenv(ENV_FILE)
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        sys.exit("GITHUB_TOKEN not set in .env (see env.example)")

    accepted = _load_accepted()
    limit = int(os.environ.get("GITHUB_SIGNALS_LIMIT", "0") or 0)
    if limit > 0:
        accepted = accepted[:limit]
    else:
        limit = len(accepted)
    cache = _load_cache()

    rows = []
    missing = 0
    for full in accepted:
        if full in cache:
            d = cache[full]
        elif full in cache and cache[full].get("_missing"):
            missing += 1
            continue
        else:
            repo, _ = _gh_get(token, f"{API}/repos/{full}")
            if repo is None:
                cache[full] = {"_missing": True}
                missing += 1
            else:
                contribs, ch = _gh_get(token, f"{API}/repos/{full}/contributors?per_page=1&anon=true")
                n_contrib = _parse_link(ch.get("Link", "")) if getattr(ch, "get", None) else 0
                if n_contrib == 0 and isinstance(contribs, list):
                    n_contrib = len(contribs)
                pulls, _ = _gh_get(token, f"{API}/search/issues?q=repo:{full}+type:pr+state:open")
                n_open_prs = (pulls or {}).get("total_count", 0)
                name = repo.get("full_name") or full
                d = {
                    "open_issues": repo.get("open_issues_count", 0),
                    "open_prs": n_open_prs,
                    "stargazers": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "contributors_approx": n_contrib,
                    "archived": bool(repo.get("archived")),
                    "has_issues": bool(repo.get("has_issues")),
                    "pushed_at": repo.get("pushed_at", ""),
                    "size_kb": repo.get("size", 0),
                }
                cache[full] = d
                time.sleep(0.2)

        if not cache[full].get("_missing"):
            rows.append({"repo": full, **cache[full]})
        CACHE.write_text(json.dumps(cache, indent=1))

    rows.sort(key=lambda r: r["repo"])
    with (OUT_DIR / "github_signals.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    print(f"[github_signals] {n}/{len(accepted)} repos with signals; "
          f"{missing} missing/deleted; wrote analysis/out/github_signals.csv")


if __name__ == "__main__":
    main()
