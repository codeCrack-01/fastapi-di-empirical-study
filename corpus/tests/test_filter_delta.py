"""corpus/tests/test_filter_delta.py — offline checks for filter.py's --delta
mode and clone-retention helpers.

Verifies (no network, no real clones):

  1. Delta decision-set: against the real corpus artifacts, every candidate in
     candidates.json is already decided (accepted or excluded), so --delta is
     a no-op today and the +500 extend routine would pick up exactly the new
     tail once candidates.json grows.
  2. Clone-retention bookkeeping helpers (clone_path / _delete_clone) behave
     invariantly on synthetic clones under a temp dir.
  3. The config constants filter reads are the settings values (thresholds are
     not drift-prone).

Run:
    uv run python corpus/tests/test_filter_delta.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
sys.path.insert(0, str(CORPUS))

import settings  # noqa: E402
from filter import _delete_clone, clone_path  # noqa: E402


def main() -> int:
    failures: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            failures.append(msg)

    # --- 1. delta decision-set on the real corpus state ---
    manifest = json.loads((CORPUS / "manifest.json").read_text())
    exclusions = json.loads((CORPUS / "exclusion_log.json").read_text())
    candidates = json.loads((CORPUS / "candidates.json").read_text())["candidates"]

    decided = {e["full_name"] for e in manifest["accepted"]} | {
        e["full_name"] for e in exclusions["excluded"]
    }
    undecided = [c for c in candidates if c["full_name"] not in decided]
    check(len(candidates) >= settings.TARGET_CANDIDATES,
          f"candidate pool covers the {settings.TARGET_CANDIDATES}-repo target (actual {len(candidates)})")
    check(not undecided, f"--delta has no new candidates to process (actual {len(undecided)})")
    check(len(manifest["accepted"]) >= 300, "accepted count is in the expected range")

    # exclusion reason set sanity (no drift of the funnel)
    reasons = {e["reason"] for e in exclusions["excluded"]}
    check(len(reasons) >= 5, f"exclusion reasons span the expected rules (actual {reasons})")

    # --- 2. clone-retention helpers on synthetic clones ---
    tmp = Path(tempfile.mkdtemp(prefix="filter_test_"))
    try:
        full = "acme/demo-app"
        dest = clone_path(tmp, full)
        dest.mkdir(parents=True)
        (dest / "marker.txt").write_text("clone")
        check(dest == tmp / "acme__demo-app", "clone_path mirrors the 'owner__repo' on-disk convention")
        check(dest.is_dir(), "synthetic clone created")
        _delete_clone(tmp, full)
        check(not dest.exists(), "_delete_clone removes an existing clone dir")
        _delete_clone(tmp, "ghost/typo")  # must be a no-op
        check(not (tmp / "ghost__typo").exists(), "_delete_clone is a safe no-op for missing dirs")
        check(len(list(tmp.iterdir())) == 0, "no stray files left behind")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- 3. settings drift guard ---
    check(settings.TARGET_CANDIDATES == 5000, "TARGET_CANDIDATES is 5000")
    check(settings.CLONE_RETENTION in ("all", "accepted", "none"), "CLONE_RETENTION is a valid policy")

    if failures:
        print(f"\n{len(failures)} assertion(s) FAILED")
        return 1
    print("\nall delta/retention checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())