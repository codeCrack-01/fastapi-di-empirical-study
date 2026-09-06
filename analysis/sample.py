"""
analysis/sample.py — Draw the study sample from the accepted corpus.

Implements the sampling rule documented in docs/methodology_notes.md:
  - exhaustive if the eligible pool N <= SAMPLE_MAX_EXHAUSTIVE,
  - otherwise a uniform random sample of SAMPLE_SIZE repos drawn with
    random.Random(SAMPLE_SEED) over the SORTED accepted names.

The sample is drawn ONCE from the pool as it stood at draw time (currently
pool_size=351) and is FROZEN thereafter. Corpus expansions after sampling do
NOT re-draw it, so repo-name-referenced manual work stays valid; the full
accepted census is the analysis universe for all reported results.

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
    ap.add_argument("--force", action="store_true",
                    help="re-draw even though a frozen sample.json already exists for a different pool")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    names = sorted(a["full_name"] for a in manifest["accepted"])
    n = len(names)
    if n == 0:
        sys.exit("no accepted repos in manifest")

    out = OUT_DIR / "sample.json"
    if out.exists():
        frozen = json.loads(out.read_text())
        if frozen.get("pool_size") != n and not args.force:
            sys.exit(
                f"refusing to re-draw: sample.json is frozen at pool_size={frozen.get('pool_size')} "
                f"(current pool {n}). The {frozen.get('sample_size')}-repo sample was drawn once for "
                "pilot/manual work and is not re-drawn on corpus expansions. Re-run with --force to "
                "explicitly replace it (invalidate prior repo-name-referenced work)."
            )

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
