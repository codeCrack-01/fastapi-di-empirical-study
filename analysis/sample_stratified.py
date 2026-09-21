"""
analysis/sample_stratified.py — Draw the star-stratified discovery sample.

Stratified random sample of the accepted corpus for the LLM pattern-discovery
phase (pattern discovery + human peer review). Stratification by GitHub stars
(docs: sampling + LLM discovery plan, 2026-09):

    S1  0 stars          (population-weighted lowest)
    S2  1-9 stars
    S3  10-99 stars      (exhaustive)
    S4  100+ stars       (exhaustive)

The small top-star strata are taken exhaustively (they hold the real DI
complexity); S2 is oversampled relative to proportional allocation so the
sample focuses weight on higher-star repos while 0-star repos remain
represented. Every member carries a reporting weight (population / sample per
stratum) so raw sample counts are never mistaken for population prevalence.

The sample is drawn ONCE (seeded, reproducible) and is FROZEN thereafter.
Output: analysis/out/sample.json (schema-versioned) + the full stratification
math in analysis/out/sample_stratification.json.

Usage:
    uv run python analysis/sample_stratified.py [--manifest corpus/manifest.json]
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

SCHEMA_VERSION = "0.2"

# Stratum definitions: (id, label, lower_stars, upper_stars) — [lower, upper)
STRATA = [
    ("S1", "0", 0, 1),
    ("S2", "1-9", 1, 10),
    ("S3", "10-99", 10, 100),
    ("S4", "100+", 100, None),
]
TARGET_SAMPLE = 327
EXHAUSTIVE = {"S3", "S4"}
# Oversample factor (2.0x proportional) applied to S2 vs S1.
OVERSAMPLE = {"S2": 2.0}

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"


def star_bin(stars: int) -> str:
    for sid, _label, lo, hi in STRATA:
        if lo <= stars and (hi is None or stars < hi):
            return sid
    return "S1"


def allocate(pop: dict[str, int], target: int, exhaustive: set[str],
             oversample: dict[str, float]) -> dict[str, int]:
    """Integer-perfect allocation: exhaustive strata first, then weighted-proportional
    across the remainder, with rounding drift fixed to the largest remainders."""
    alloc = {}
    remaining = target
    for sid in exhaustive:
        alloc[sid] = pop[sid]
        remaining -= pop[sid]

    rest = [s for s in pop if s not in exhaustive]
    if not rest:
        assert remaining == 0, f"target {target} not met by exhaustive strata"
        return alloc

    w = {s: (oversample[s] if s in oversample else 1.0) for s in rest}
    num = {s: pop[s] * w[s] for s in rest}
    denom = sum(num.values())
    raw = {s: remaining * num[s] / denom for s in rest}
    base = {s: int(raw[s]) for s in rest}
    leftover = remaining - sum(base.values())
    # Give the leftover slots to the strata with the largest fractional remainders.
    order = sorted(rest, key=lambda s: raw[s] - base[s], reverse=True)
    for s in order[:leftover]:
        base[s] += 1
    for s in rest:
        alloc[s] = base[s]
    assert sum(alloc.values()) == target, f"allocation sums to {sum(alloc.values())}, want {target}"
    for s in alloc:
        assert alloc[s] <= pop[s], f"{s}: allocated {alloc[s]} > population {pop[s]}"
    return alloc


def main():
    ap = argparse.ArgumentParser(description="Draw the star-stratified discovery sample")
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--target", type=int, default=TARGET_SAMPLE)
    ap.add_argument("--force", action="store_true",
                    help="re-draw even though a frozen stratified sample.json already exists")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    entries = manifest["accepted"]

    pop: dict[str, int] = {s: 0 for s, *_ in STRATA}
    by_stratum: dict[str, list[str]] = {s: [] for s, *_ in STRATA}
    for e in entries:
        sid = star_bin(int(e.get("stars_gh") or 0))
        pop[sid] += 1
        by_stratum[sid].append(e["full_name"])

    alloc = allocate(pop, args.target, EXHAUSTIVE, OVERSAMPLE)

    # Deterministic draw within each stratum over SORTED names.
    rng = random.Random(SAMPLE_SEED)
    weights: dict[str, float] = {}
    sampled: list[dict] = []
    for sid, label, _lo, _hi in STRATA:
        n_pop, n_smp = pop[sid], alloc[sid]
        names = sorted(by_stratum[sid])
        chosen = sorted(rng.sample(names, n_smp)) if n_smp < n_pop else list(names)
        weights[sid] = round(n_pop / n_smp, 6) if n_smp else 0.0
        for name in chosen:
            sampled.append({"full_name": name, "stratum": sid, "weight": weights[sid]})
    sampled = sorted(sampled, key=lambda r: r["full_name"])

    out = OUT_DIR / "sample.json"
    if out.exists() and not args.force:
        frozen = json.loads(out.read_text())
        if frozen.get("schema_version") == SCHEMA_VERSION:
            sys.exit(
                f"refusing to re-draw: {out} is a frozen stratified sample "
                f"(pool_size={frozen.get('pool_size')}). Re-run with --force to replace it."
            )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "stratified_random",
        "seed": SAMPLE_SEED,
        "strata": [
            {"id": sid, "label": label, "population": pop[sid],
             "sample": alloc[sid], "weight": weights[sid]}
            for sid, label, *_ in STRATA
        ],
        "pool_size": sum(pop.values()),
        "sample_size": len(sampled),
        "sampled": sampled,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(payload, indent=2))

    stratification = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": payload["generated_at"],
        "target": args.target,
        "seed": SAMPLE_SEED,
        "allocation": {
            s: {"population": pop[s], "allocated": alloc[s],
                "coverage_pct": round(100 * alloc[s] / pop[s], 2)}
            for s, *_ in STRATA
        },
        "notes": {
            "exhaustive_strata": sorted(EXHAUSTIVE),
            "oversample_factors": dict(OVERSAMPLE),
            "remainder_fix": "rounding drift assigned to largest fractional remainders",
        },
    }
    Path(OUT_DIR / "sample_stratification.json").write_text(json.dumps(stratification, indent=2))

    print(f"[sample] pool N={sum(pop.values())}, seed={SAMPLE_SEED} -> {len(sampled)} repos")
    for s in STRATA:
        print(f"  {s[0]} ({s[1]:>5}) pop={pop[s[0]]:>5} smp={alloc[s[0]]:>4} "
              f"w={weights[s[0]]:.3f} cov={100*alloc[s[0]]/pop[s[0]]:.1f}%")
    print(f"[sample] wrote {out}")
    print(f"[sample] wrote {OUT_DIR / 'sample_stratification.json'}")


if __name__ == "__main__":
    main()