"""
corpus/finder.py — Candidate discovery for the FastAPI DI corpus.

Stage 1 of the corpus methodology.

Primary source : GitHub's dependency-graph dependents list of `fastapi/fastapi`
                 (repos whose manifests GitHub's dependency graph resolves as
                 depending on fastapi). Scraped from the public "Used by" page:
                 https://github.com/fastapi/fastapi/network/dependents
Secondary     : GitHub REST API enrichment of each candidate (fork/archived/
                 pushed_at/created_at/languages/commits).

Why not Libraries.io: its `/dependents` API is disabled server-side
("Disabled for performance reasons"), so GitHub's own dependency graph is used
as the live equivalent. This is documented as a methodology note.

Outputs corpus/candidates.json — raw, unfiltered candidates with metadata.
Snapshots raw HTML pages to corpus/raw_dependents/ for reproducibility.
Resumable: enrichment progress is checkpointed to candidates.partial.json;
re-running skips already-enriched repos and continues where it left off.

Usage:
    export GITHUB_TOKEN=...
    python corpus/finder.py --target 5000 --output corpus/candidates.json
    python corpus/finder.py --target 5000 --include-topic corpus/topic_seed.json
    python corpus/finder.py --skip-scrape   # offline: replay saved pages only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

from settings import (
    CORPUS_SCHEMA_VERSION,
    DEPENDENTS_MAX_PAGES,
    DEPENDENTS_PAGE_DELAY_SEC,
    TARGET_CANDIDATES,
)

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT.parent / ".env"
load_dotenv(ENV_FILE)

GITHUB_API = "https://api.github.com"
DEPENDENTS_URL = "https://github.com/fastapi/fastapi/network/dependents"

DEPENDENTS_ROW_RE = re.compile(
    r'data-test-id="dg-repo-pkg-dependent".*?<a class="text-bold"[^>]*href="/([^"]+)"',
    re.S,
)
NEXT_CURSOR_RE = re.compile(
    r'href="[^"]*dependents_after=([A-Za-z0-9_=-]+)"[^>]*>Next<'
)


class APIError(Exception):
    pass


class RateLimitError(APIError):
    pass


class WatchdogTimeout(Exception):
    pass


WATCHDOG_SECS = 300


def _alarm_handler(signum, frame):
    raise WatchdogTimeout(f"per-repo watchdog timed out after {WATCHDOG_SECS}s")


RETRYABLE = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


def _gh_request(token: str, url: str, params: Optional[dict] = None, attempts: int = 4) -> requests.Response:
    """GET with retry/backoff for dropped connections, timeouts, and 5xx."""
    last = None
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(url, headers=gh_headers(token), params=params, timeout=60)
            if resp.status_code in (500, 502, 503, 504) and attempt < attempts:
                time.sleep(2 ** attempt)
                continue
            return resp
        except RETRYABLE as exc:
            last = exc
            if attempt < attempts:
                print(f"[finder] connection error on {url} (attempt {attempt}): {exc}")
                time.sleep(2 ** attempt)
    raise APIError(f"GitHub request failed after {attempts} attempts: {last}")


def scrape_dependents_pages(
    max_pages: int,
    delay: float = 1.0,
    min_count: Optional[int] = None,
    from_cache: bool = False,
) -> list[str]:
    """Return owner/repo full names from the GitHub dependents HTML.

    Pages are paginated newest-candidate-first; when ``min_count`` is given the
    crawl stops as soon as ``min_count`` unique repos are scraped (best-effort:
    end-of-pagination and HTTP 429 stay hard stops). Each fetched page is
    snapshotted to ``corpus/raw_dependents/`` for reproducibility.

    With ``from_cache`` the already-snapshotted pages are replayed first (offline
    resume / verification), then — if ``min_count`` is not yet met — the crawl
    continues live from the last cached page's cursor, adding only the missing
    tail instead of re-fetching every page.
    """
    raw_dir = ROOT / "raw_dependents"
    raw_dir.mkdir(exist_ok=True)
    repos: list[str] = []
    seen: set[str] = set()
    cursor: Optional[str] = None
    start_page = 1

    if from_cache:
        pages = sorted(
            raw_dir.glob("dependents_page_*.html"),
            key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
        )
        for page in pages:
            html = page.read_text(encoding="utf-8", errors="replace")
            added = [r for r in DEPENDENTS_ROW_RE.findall(html) if r not in seen]
            repos.extend(added)
            seen.update(added)
            m = NEXT_CURSOR_RE.search(html)
            cursor = m.group(1) if m else cursor
        if pages:
            start_page = len(pages) + 1
        print(f"[finder] replayed {len(repos)} repos from {len(pages)} cached pages")
        if min_count is not None and len(repos) >= min_count:
            print(f"[finder] cache alone meets target ({min_count}); no live fetch needed")
            return repos

    for page in range(start_page, max_pages + 1):
        url = DEPENDENTS_URL + (f"?dependents_after={cursor}" if cursor else "")
        resp = requests.get(url, timeout=60)
        if resp.status_code == 429 or resp.status_code == 403:
            print(f"[finder] HTTP {resp.status_code} at page {page}; stopping pagination")
            break
        if resp.status_code >= 400:
            raise APIError(f"Dependents page error {resp.status_code}: {resp.text[:200]}")
        html = resp.text
        (raw_dir / f"dependents_page_{page:03d}.html").write_text(html)
        rows = DEPENDENTS_ROW_RE.findall(html)
        added = [r for r in rows if r not in seen]
        repos.extend(added)
        seen.update(added)
        m = NEXT_CURSOR_RE.search(html)
        if not m:
            print(f"[finder] reached last dependents page at page {page}")
            break
        cursor = m.group(1)
        print(f"[finder] dependents page {page}: +{len(added)} (cumulative {len(repos)})")
        if min_count is not None and len(repos) >= min_count:
            print(f"[finder] reached scrape target ({min_count} unique repos) at page {page}")
            break
        time.sleep(delay)
    return repos


def gh_headers(token: str) -> dict:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def gh_get(token: str, url: str, params: Optional[dict] = None) -> dict:
    resp = _gh_request(token, url, params)
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        raise RateLimitError("GitHub rate limit hit")
    if resp.status_code == 404:
        raise APIError("GitHub 404 not found")
    if resp.status_code >= 400:
        raise APIError(f"GitHub error {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def gh_get_commits(token: str, owner: str, repo: str) -> int:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    resp = _gh_request(token, url, {"per_page": 1})
    link = resp.headers.get("Link", "")
    last_match = re.search(r'page=(\d+)>;\s*rel="last"', link)
    if last_match:
        return int(last_match.group(1))
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        raise RateLimitError("GitHub rate limit hit")
    if resp.status_code >= 400:
        return 0
    return len(resp.json())


def gh_get_languages(token: str, owner: str, repo: str) -> dict[str, int]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/languages"
    return gh_get(token, url)


def enrich_candidate(token: str, full_name: str) -> Optional[dict]:
    owner, name = full_name.split("/", 1)
    try:
        meta = gh_get(token, f"{GITHUB_API}/repos/{owner}/{name}")
        langs = gh_get_languages(token, owner, name)
        commits = gh_get_commits(token, owner, name)
    except RateLimitError:
        raise
    except APIError:
        return None
    total_bytes = sum(langs.values())
    py_ratio = round(langs.get("Python", 0) / total_bytes, 4) if total_bytes else 0.0
    return {
        "full_name": full_name,
        "repository_url": f"https://github.com/{full_name}",
        "description_libio": None,
        "stars_libio": None,
        "forks_libio": None,
        "name": name,
        "description_gh": meta.get("description"),
        "stars_gh": meta.get("stargazers_count"),
        "forks_gh": meta.get("forks_count"),
        "language": meta.get("language"),
        "fork": meta.get("fork", False),
        "archived": meta.get("archived", False),
        "pushed_at": meta.get("pushed_at"),
        "created_at": meta.get("created_at"),
        "updated_at": meta.get("updated_at"),
        "default_branch": meta.get("default_branch"),
        "size_kb": meta.get("size"),
        "license": (meta.get("license") or {}).get("spdx_id"),
        "topics": meta.get("topics", []),
        "py_ratio": py_ratio,
        "languages_bytes": langs,
        "commit_count": commits,
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Discover FastAPI candidate repos from GitHub dependents"
    )
    parser.add_argument("--output", default=str(ROOT / "candidates.json"))
    parser.add_argument(
        "--target",
        type=int,
        default=TARGET_CANDIDATES,
        help="Stop once this many unique repos are scraped (best-effort; default %(default)s)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEPENDENTS_MAX_PAGES,
        help="Absolute safety cap on dependents pages (30 repos/page)",
    )
    parser.add_argument(
        "--page-delay", type=float, default=DEPENDENTS_PAGE_DELAY_SEC, help="Seconds between page fetches"
    )
    parser.add_argument(
        "--include-topic",
        default="",
        metavar="TOPIC_SEED.json",
        help="Optional topic:fastapi seed file whose repos are unioned into the candidate pool",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Replay already-snapshotted dependents pages from corpus/raw_dependents/ instead of fetching",
    )
    args = parser.parse_args()

    gh_token = os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        sys.exit("GITHUB_TOKEN env var is required (see env.example)")

    out_path = Path(args.output)
    partial_path = out_path.with_suffix(".partial.json")

    def load_existing(path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text()).get("candidates", [])
        except (json.JSONDecodeError, OSError):
            return []

    existing = load_existing(partial_path) or load_existing(out_path)
    enriched = list(existing)
    done = {c["full_name"] for c in enriched}

    full_names = scrape_dependents_pages(
        args.max_pages, args.page_delay, min_count=args.target, from_cache=args.skip_scrape
    )
    if args.include_topic:
        topic = json.loads(Path(args.include_topic).read_text()).get("seed", [])
        topic_names = [t["full_name"] for t in topic]
        before = len(full_names)
        full_names.extend(n for n in topic_names if n not in full_names)
        print(f"[finder] topic union (+{len(full_names) - before} repos from {args.include_topic})")
    pending = [f for f in full_names if f not in done]
    print(
        f"[finder] {len(full_names)} scraped/union; {len(enriched)} already enriched; "
        f"{len(pending)} pending"
    )

    def checkpoint() -> None:
        partial_path.write_text(
            json.dumps(
                {
                    "schema_version": CORPUS_SCHEMA_VERSION,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "github dependency-graph dependents of fastapi/fastapi",
                    "raw_html_dir": str(ROOT / "raw_dependents"),
                    "candidates": enriched,
                },
                indent=2,
            )
        )

    signal.signal(signal.SIGALRM, _alarm_handler)

    try:
        for i, full_name in enumerate(pending):
            signal.alarm(WATCHDOG_SECS)
            try:
                entry = enrich_candidate(gh_token, full_name)
            except RateLimitError as exc:
                checkpoint()
                print(
                    f"[finder] rate limit reached ({exc}); saved {len(enriched)} "
                    f"to {partial_path} — re-run to resume"
                )
                sys.exit(0)
            except WatchdogTimeout:
                print(f"[finder] watchdog timeout on {full_name}; leaving for next run")
                continue
            finally:
                signal.alarm(0)
            if entry is not None:
                enriched.append(entry)
            if i % 50 == 0 and i > 0:
                checkpoint()
                print(f"[finder] checkpoint {len(enriched)} candidates")
            time.sleep(0.4)
    except KeyboardInterrupt:
        checkpoint()
        print(f"[finder] interrupted; saved {len(enriched)} candidates to {partial_path}")
        sys.exit(130)

    payload = {
        "schema_version": CORPUS_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "github dependency-graph dependents of fastapi/fastapi",
        "raw_html_dir": str(ROOT / "raw_dependents"),
        "candidates": enriched,
    }
    out_path.write_text(json.dumps(payload, indent=2))
    if partial_path.exists():
        partial_path.unlink()
    status = "TARGET MET" if len(enriched) >= args.target else "BEST EFFORT (target not met)"
    print(f"[finder] {status}: {len(enriched)} / {args.target} candidates -> {out_path}")


if __name__ == "__main__":
    main()
