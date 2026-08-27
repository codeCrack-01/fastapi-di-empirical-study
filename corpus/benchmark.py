"""
corpus/benchmark.py — Independent-signal recall benchmark.

The corpus pool is built from GitHub's dependency-graph dependents list.
This script pulls an *independent* discovery signal — the `topic:fastapi`
repository search — and measures its overlap with the pool. The overlap
quantifies how much of the dependency-graph pool an alternative signal would
have recovered, bounding the completeness/recall of the primary source.

Subcommands
-----------
seed     Fetch and snapshot the `topic:fastapi` search results.
overlap  Report overlap stats vs candidates.json and manifest.json.

Usage:
    export GITHUB_TOKEN=...
    python corpus/benchmark.py seed   --output corpus/topic_seed.json --top 1000
    python corpus/benchmark.py overlap --topic corpus/topic_seed.json \
        --candidates corpus/candidates.json --manifest corpus/manifest.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

from settings import TOPIC_QUERY, TOPIC_SEED_TOP

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT.parent / ".env"
load_dotenv(ENV_FILE)

GITHUB_API = "https://api.github.com"
SORT = "stars"
ORDER = "desc"


def gh_headers(token: str) -> dict:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_topic_seed(token: str, top: int = 1000) -> list[dict]:
    results: list[dict] = []
    page = 1
    while len(results) < top:
        resp = requests.get(
            f"{GITHUB_API}/search/repositories",
            headers=gh_headers(token),
            params={
                "q": TOPIC_QUERY,
                "sort": SORT,
                "order": ORDER,
                "per_page": 100,
                "page": page,
            },
            timeout=60,
        )
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            print("[benchmark] search rate limit hit; stopping")
            break
        if resp.status_code >= 400:
            print(f"[benchmark] search error {resp.status_code}: {resp.text[:200]}")
            break
        body = resp.json()
        items = body.get("items", [])
        if not items:
            break
        for it in items:
            results.append(
                {
                    "full_name": it["full_name"],
                    "stars": it["stargazers_count"],
                    "description": it.get("description"),
                }
            )
        print(f"[benchmark] topic seed page {page}: +{len(items)} (cumulative {len(results)})")
        page += 1
        time.sleep(2.2)
    return results


def cmd_seed(args: argparse.Namespace):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN env var is required")
    seed = fetch_topic_seed(token, args.top)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": f"{TOPIC_QUERY}  sort={SORT} order={ORDER}",
        "top": len(seed),
        "seed": seed,
    }
    out = Path(args.output)
    out.write_text(json.dumps(payload, indent=2))
    print(f"[benchmark] wrote {len(seed)} topic-seed repos to {out}")


def _full_names(payload: dict, key: str) -> set[str]:
    return {c["full_name"] for c in payload.get(key, [])}


def cmd_overlap(args: argparse.Namespace):
    topic = json.loads(Path(args.topic).read_text())
    topic_names = {r["full_name"] for r in topic.get("seed", [])}
    print(f"topic seed size: {len(topic_names)}")

    candidates = json.loads(Path(args.candidates).read_text())
    cand_names = _full_names(candidates, "candidates")
    cand_hit = cand_names & topic_names
    print(
        f"candidates:        {len(cand_names):>6}  in topic: {len(cand_hit):>6}  "
        f"({100*len(cand_hit)/max(len(cand_names),1):.1f}%)"
    )

    if args.manifest and Path(args.manifest).exists():
        manifest = json.loads(Path(args.manifest).read_text())
        acc_names = {a["full_name"] for a in manifest.get("accepted", [])}
        acc_hit = acc_names & topic_names
        print(
            f"accepted:          {len(acc_names):>6}  in topic: {len(acc_hit):>6}  "
            f"({100*len(acc_hit)/max(len(acc_names),1):.1f}%)"
        )
        missing = sorted(acc_names - topic_names)
        if missing:
            print("accepted repos NOT found by topic signal (dependency-graph-only):")
            for m in missing:
                print(f"  - {m}")
    else:
        print("(no manifest supplied / not found; skipping accepted overlap)")


def main():
    parser = argparse.ArgumentParser(description="Independent-signal recall benchmark")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_seed = sub.add_parser("seed", help="Fetch topic:fastapi search seed")
    p_seed.add_argument("--output", default=str(ROOT / "topic_seed.json"))
    p_seed.add_argument("--top", type=int, default=TOPIC_SEED_TOP)
    p_seed.set_defaults(func=cmd_seed)

    p_overlap = sub.add_parser("overlap", help="Compute overlap vs pool")
    p_overlap.add_argument("--topic", default=str(ROOT / "topic_seed.json"))
    p_overlap.add_argument("--candidates", default=str(ROOT / "candidates.json"))
    p_overlap.add_argument("--manifest", default=str(ROOT / "manifest.json"))
    p_overlap.set_defaults(func=cmd_overlap)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
