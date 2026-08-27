"""
analysis/sample.py — Draw the study sample from the accepted corpus.

Implements the sampling rule documented in docs/methodology_notes.md:
  - exhaustive if the eligible pool N <= SAMPLE_MAX_EXHAUSTIVE,
  - otherwise a uniform random sample of SAMPLE_SIZE repos drawn with
    random.Random(SAMPLE_SEED) over the SORTED accepted names.

Sorting before drawing guarantees the superset property: the sample for a
smaller pool is always a subset of the sample for any larger pool drawn
with the same seed, so later corpus expansions never invalidate earlier
manual work.

Output: analysis/out/sample.json (schema-versioned, reproducible).

Usage:
    uv run python analysis/sample.py [--manifest corpus/manifest.json]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "corpus"))
from settings import SAMPLE_SEED  # noqa: E402

SCHEMA_VERSION = "0.1"
SAMPLE_SIZE = 100
SAMPLE_MAX_EXHAUSTIVE = 100

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"


def main():
    ap = argparse.ArgumentParser(description="Draw the study sample")
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--size", type=int, default=SAMPLE_SIZE)
    ap.add_argument("--max-exhaustive", type=int, default=SAMPLE_MAX_EXHAUSTIVE)
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    names = sorted(a["full_name"] for a in manifest["accepted"])
    n = len(names)
    if n == 0:
        sys.exit("no accepted repos in manifest")

    if n <= args.max_exhaustive:
        method = "exhaustive"
        sampled = list(names)
        seed_used = None
    else:
        method = "random"
        seed_used = SAMPLE_SEED
        sampled = sorted(random.Random(SAMPLE_SEED).sample(names, args.size))

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "seed": seed_used,
        "pool_size": n,
        "sample_size": len(sampled),
        "sampled": sampled,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "sample.json"
    out.write_text(json.dumps(payload, indent=2))
    print(
        f"[sample] pool N={n}, method={method}"
        + (f" (seed={seed_used})" if seed_used is not None else "")
        + f" -> {len(sampled)} repos written to {out}"
    )


if __name__ == "__main__":
    main()
