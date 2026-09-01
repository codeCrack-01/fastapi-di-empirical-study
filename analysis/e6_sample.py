"""
analysis/e6_sample.py — randomized stratified subsample for E6 human review.

Draws a representative, fixed-seed subsample from the E6-flagged pool and an
equal-sized unflagged control group. Flagged repos are stratified by
{stars bucket} x {marker count bucket}; control repos by {stars bucket} only.
Allocation is proportional to stratum size, with remainders going to the
largest strata. Draws are recorded with seed + per-stratum sizes for audit
and reproducibility.

Usage:
    uv run python analysis/e6_sample.py
Outputs:
    analysis/out/e6_subsample.csv         repo, group, stars, markers, order
    analysis/out/e6_subsample_audit.json  seed, per-stratum n_total/n_drawn
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

SEED = 20260817
TARGET_PER_POOL = 24


def _stars_bucket(stars) -> str:
    stars = stars or 0
    if stars <= 0:
        return "0"
    if stars < 10:
        return "1-9"
    if stars < 100:
        return "10-99"
    return "100+"


def _marker_bucket(count: int) -> str:
    return "2+" if count > 1 else "1"


def _draw_strata(pool: list[dict], rng: random.Random, per_pool: int, flag: bool) -> tuple[list[dict], dict]:
    if flag:
        strata: dict[tuple[str, str], list[dict]] = {}
        for r in pool:
            strata.setdefault((_stars_bucket(r["stars_gh"]), _marker_bucket(r["marker_count"])), []).append(r)
        stratum_label = lambda s: (s[0], s[1])
    else:
        strata = {}
        for r in pool:
            strata.setdefault((_stars_bucket(r["stars_gh"]), "n/a"), []).append(r)
        stratum_label = lambda s: s

    strata = dict(sorted(strata.items(), key=lambda kv: (-len(kv[1]), str(kv[0]))))
    total = sum(len(v) for v in strata.values())
    base = {s: (per_pool * len(v)) // total for s, v in strata.items()}
    assigned = sum(base.values())
    order = sorted(strata, key=lambda s: (-len(strata[s]), str(s)))
    i = 0
    while assigned < per_pool and i < len(order):
        s = order[i]
        if base[s] < len(strata[s]):
            base[s] += 1
            assigned += 1
        i += 1

    drawn: list[dict] = []
    meta = {}
    for s in order:
        members = list(strata[s])
        rng.shuffle(members)
        n = min(base[s], len(members))
        chosen = members[:n]
        for c in chosen:
            drawn.append(c)
        meta[str(stratum_label(s))] = {"n_total": len(members), "n_drawn": n}
    rng.shuffle(drawn)  # final order is presentation order for blinded review
    return drawn, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--out", default=str(OUT_DIR / "e6_subsample.csv"))
    ap.add_argument("--audit", default=str(OUT_DIR / "e6_subsample_audit.json"))
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--target-per-pool", type=int, default=TARGET_PER_POOL)
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(Path(args.manifest).read_text())
    flagged, control = [], []
    for r in manifest["accepted"]:
        mk = len(r.get("tutorial_markers", "").split(",")) if r.get("tutorial_markers") else 0
        entry = {
            "repo": r["full_name"],
            "stars_gh": r.get("stars_gh") or 0,
            "marker_count": mk if r.get("tutorial_flag") else 0,
            "tutorial_flag": bool(r.get("tutorial_flag")),
        }
        (flagged if entry["tutorial_flag"] else control).append(entry)

    rng = random.Random(args.seed)
    drawn_flag, meta_flag = _draw_strata(flagged, rng, args.target_per_pool, True)
    drawn_ctrl, meta_ctrl = _draw_strata(control, rng, args.target_per_pool, False)

    rows = [
        {"repo": r["repo"], "group": "flag", "stars_gh": r["stars_gh"],
         "marker_count": r["marker_count"], "order": i}
        for i, r in enumerate(drawn_flag)
    ] + [
        {"repo": r["repo"], "group": "control", "stars_gh": r["stars_gh"],
         "marker_count": 0, "order": i}
        for i, r in enumerate(drawn_ctrl)
    ]

    audit = {
        "seed": args.seed,
        "target_per_pool": args.target_per_pool,
        "flag_pool_total": len(flagged),
        "control_pool_total": len(control),
        "flag_strata": meta_flag,
        "control_strata": meta_ctrl,
    }
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["repo", "group", "stars_gh", "marker_count", "order"])
        w.writeheader()
        w.writerows(rows)
    Path(args.audit).write_text(json.dumps(audit, indent=2))

    print(f"[e6_sample] seed={args.seed} -> flag: {len(drawn_flag)}, control: {len(drawn_ctrl)}")
    for label, meta in (("flag", meta_flag), ("control", meta_ctrl)):
        for s, v in meta.items():
            print(f"  [{label}] {s}: {v['n_drawn']}/{v['n_total']}")
    print(f"  -> {args.out}")

    # print the presentation order (blinded: group hidden)
    print("\nreview order (no group shown during label pass):")
    for i, r in enumerate(rows):
        print(f"  {i:2d}. {r['repo']}")


if __name__ == "__main__":
    main()