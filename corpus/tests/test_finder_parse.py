"""corpus/tests/test_finder_parse.py — offline replay of the saved dependents HTML.

Feeds the 150 snapshotted GitHub "Used by" pages through finder's parsers and
asserts the invariants the live crawl relies on:

  1. the row regex extracts a determinate set of unique repos;
  2. the recorded tail (page 150) still carries a "Next" cursor, i.e. the
     dependents list was NOT exhausted at the old 4,500 cap — headroom for
     growing the pool (e.g. 4,500 -> 5,000 candidates);
  3. cross-page duplicates collapse deterministically (byte-stable).

No network is used. Run:
    uv run python corpus/tests/test_finder_parse.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
sys.path.insert(0, str(CORPUS))

import finder  # noqa: E402

RAW_DIR = CORPUS / "raw_dependents"


def replay_pages() -> tuple[list[str], int, bool]:
    repos: list[str] = []
    seen: set[str] = set()
    n_pages = 0
    last_cursor: str | None = None
    pages = sorted(
        RAW_DIR.glob("dependents_page_*.html"),
        key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
    )
    for page in pages:
        n_pages += 1
        html = page.read_text(encoding="utf-8", errors="replace")
        added = [r for r in finder.DEPENDENTS_ROW_RE.findall(html) if r not in seen]
        repos.extend(added)
        seen.update(added)
        m = finder.NEXT_CURSOR_RE.search(html)
        last_cursor = m.group(1) if m else None
    return repos, n_pages, last_cursor is not None


def main() -> int:
    failures: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            failures.append(msg)

    repos1, n1, has_next1 = replay_pages()
    repos2, n2, has_next2 = replay_pages()

    check(len(list(RAW_DIR.glob("dependents_page_*.html"))) >= 100, "at least 100 dependents pages are archived")
    check(n1 >= 140, f"all expected pages replayed ({n1})")
    check(len(repos1) >= 4490, f"row regex recovers >= 4490 unique repos (actual {len(repos1)})")
    check(has_next1, "recorded tail page still has a Next cursor (discovery headroom exists)")
    check(repos1 == repos2 and has_next1 == has_next2, "parsing is deterministic across passes")
    check(
        len(repos1) == len(set(repos1)),
        "no duplicate owner/repo within the replay (cross-page dedupe stable)",
    )
    check(n1 == n2, "page counts agree across passes")

    if failures:
        print(f"\n{len(failures)} assertion(s) FAILED")
        return 1
    print(f"\nall checks passed; {len(repos1)} unique repos recoverable offline")
    return 0


if __name__ == "__main__":
    sys.exit(main())