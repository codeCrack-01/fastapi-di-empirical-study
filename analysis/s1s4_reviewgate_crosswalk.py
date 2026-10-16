#!/usr/bin/env python3
"""analysis/s1s4_reviewgate_crosswalk.py — S1-S4 verdict distribution over the
ReviewGate C1-C4 ecological arms (the *analytical* half of ReviewGate).

ReviewGate has two halves (see docs/reviewgate_experiment_final.md):
  A. analytical — corpus-level construct co-occurrence -> ecological groups ->
     strategy crosswalk (THIS SCRIPT);
  B. measured  — ReviewGate-R app, arms = C1-C4 spellings
     (docs/c1c4_construct_results.md).

This script partitions every accepted repository by its exact C1-C4 presence
bitmask (the ecological partition the ReviewGate design uses), classifies each
with extractor.verdict.classify_report (canonical precedence S4 > S2 > S3 > S1),
and reports the S1-S4 distribution overall and per ecological group, for both
the frozen v0.4 reports and the current v0.5 reports.

Writes:
  analysis/out/s1s4_reviewgate_crosswalk.json
  docs/s1s4_reviewgate_results.md

Usage:
    .venv/bin/python analysis/s1s4_reviewgate_crosswalk.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extractor"))
from models import RepoReport  # noqa: E402
from verdict import classify_report  # noqa: E402

S = ["S1", "S2", "S3", "S4"]
REPORTS = {"v0.4": ROOT / "corpus" / "reports_v0.4",
           "v0.5": ROOT / "corpus" / "reports_v0.5"}
OUT_JSON = ROOT / "analysis" / "out" / "s1s4_reviewgate_crosswalk.json"
OUT_MD = ROOT / "docs" / "s1s4_reviewgate_results.md"

GROUP_ORDER = ["c0_none", "c1_pure", "c2_pure", "dy", "ad", "ady", "other"]
GROUP_LABEL = {
    "c0_none": "c0_none",
    "c1_pure": "c1_pure (C1 only, `Depends`)",
    "c2_pure": "c2_pure (C2 only, `Security`)",
    "dy": "dy (C1+C4, `Depends`+yield)",
    "ad": "ad (C1+C3, `Annotated`+`Depends`)",
    "ady": "ady (C1+C3+C4)",
    "other": "other (any other mix)",
}

# exact C1-C4 presence bitmask (c1,c2,c3,c4) -> ecological group
BITMASK = {
    (0, 0, 0, 0): "c0_none",
    (1, 0, 0, 0): "c1_pure",
    (0, 1, 0, 0): "c2_pure",
    (1, 0, 0, 1): "dy",
    (1, 0, 1, 0): "ad",
    (1, 0, 1, 1): "ady",
}


def bits_and_group(agg) -> tuple[tuple[int, int, int, int], str]:
    bits = (int(agg.depends_total > 0), int(agg.security_total > 0),
            int(agg.annotated_depends_total > 0), int(agg.yield_dep_total > 0))
    return bits, BITMASK.get(bits, "other")


def collect(d: Path):
    """-> (overall, {group: Counter}, {bitmask: count}, {repo: bitmask}, n)"""
    overall = Counter()
    by_group = {g: Counter() for g in GROUP_ORDER}
    by_bits, by_repo = Counter(), {}
    n = 0
    for f in sorted(d.glob("*.json")):
        r = RepoReport.model_validate(json.loads(f.read_text()))
        bits, g = bits_and_group(r.aggregate)
        lab = classify_report(r).label
        overall[lab] += 1
        by_group[g][lab] += 1
        by_bits["".join(map(str, bits))] += 1
        by_repo[f.stem] = "".join(map(str, bits))
        n += 1
    return overall, by_group, by_bits, by_repo, n


def pct(c: int, n: int) -> str:
    return f"{100 * c / n:.1f}%" if n else "—"


def dist_row(label: str, c: Counter, n: int, star: bool = False) -> str:
    cells = " | ".join(f"{c.get(s, 0)} ({pct(c.get(s, 0), n)})" for s in S)
    name = f"**{label}**" if star else label
    return f"| {name} | {cells} | {n} |"


def main() -> None:
    data = {}
    for ver, d in REPORTS.items():
        overall, by_group, by_bits, by_repo, n = collect(d)
        data[ver] = {"n": n, "overall": dict(overall),
                     "by_group": {g: dict(by_group[g]) for g in GROUP_ORDER},
                     "group_n": {g: sum(by_group[g].values()) for g in GROUP_ORDER},
                     "by_bits": dict(by_bits), "by_repo": by_repo}
        print(f"[{ver}] n={n} overall={dict(overall)}")

    # constructs are *nearly* stable across schemas; a few repos re-extract
    changed = sorted(
        r for r in set(data["v0.4"]["by_repo"]) | set(data["v0.5"]["by_repo"])
        if data["v0.4"]["by_repo"].get(r) != data["v0.5"]["by_repo"].get(r))
    print(f"repos whose C1-C4 bitmask changed v0.4->v0.5: {len(changed)}")

    OUT_JSON.write_text(json.dumps(data, indent=2))
    write_md(data, changed)
    print("wrote", OUT_JSON.relative_to(ROOT))
    print("wrote", OUT_MD.relative_to(ROOT))


def write_md(data, changed) -> None:
    n4, n5 = data["v0.4"]["n"], data["v0.5"]["n"]
    o4, o5 = Counter(data["v0.4"]["overall"]), Counter(data["v0.5"]["overall"])
    L = [
        "# S1–S4 ReviewGate Results — strategy verdicts over the C1–C4 ecological arms",
        "",
        "Status: **analytical crosswalk, corpus-level** (no execution). The *measured*",
        "ReviewGate experiment is the C1–C4 spelling run in",
        "`docs/c1c4_construct_results.md`; this document is the S1–S4 side of the",
        "ReviewGate analytical half (corpus co-occurrence → ecological groups →",
        "strategy verdict).",
        "",
        "Canonical precedence: **`S4 > S2 > S3 > S1`** (evidence-first;",
        "`extractor/verdict.py`). Generated by `analysis/s1s4_reviewgate_crosswalk.py`;",
        "numbers in `analysis/out/s1s4_reviewgate_crosswalk.json`.",
        "",
        "---",
        "",
        "## 1. Scope",
        "",
        "- **In:** the distribution of S1–S4 verdicts over the ReviewGate ecological",
        "  groups (`c0_none`, `c1_pure`, `c2_pure`, `dy`, `ad`, `ady`, `other`), for",
        "  the frozen v0.4 reports and the current v0.5 reports.",
        "- **Out:** latency/throughput results. S1–S4 *measured* behaviour lives in",
        "  Tier-1 (`analysis/syncasync/results_5arm_final.md`, `docs/results*.md`);",
        "  ReviewGate itself was only *executed* for C1–C4 spellings.",
        "",
        "## 2. Definitions and precedence",
        "",
        "| label | meaning |",
        "|---|---|",
        "| C1 | `Depends(...)` |",
        "| C2 | `Security(...)` |",
        "| C3 | `Annotated[T, Depends(...)]` |",
        "| C4 | generator / `yield` dependency |",
        "",
        "| label | strategy |",
        "|---|---|",
        "| S1 | no DI detected (residual) |",
        "| S2 | FastAPI framework DI (any core C1–C3) |",
        "| S3 | manual / hand-rolled DI evidence only |",
        "| S4 | third-party container wired into the request path |",
        "",
        "**Precedence:** `S4 > S2 > S3 > S1`. Any group containing a core construct",
        "(C1–C3) therefore classifies essentially entirely as **S2**; S3 survives only",
        "where manual evidence exists *without* core DI; S1 is the residual.",
        "",
        "## 3. Ecological group partition",
        "",
        "Groups are the **exact C1–C4 presence bitmask** per repository (not a",
        "dominance rule):",
        "",
        "| bitmask (C1,C2,C3,C4) | group |",
        "|---|---|",
        "| 0000 | `c0_none` |",
        "| 1000 | `c1_pure` |",
        "| 0100 | `c2_pure` |",
        "| 1001 | `dy` |",
        "| 1010 | `ad` |",
        "| 1011 | `ady` |",
        "| everything else | `other` |",
        "",
        "Group sizes are *nearly* identical under v0.4 and v0.5 (constructs are",
        "mostly stable across the two schemas; only the S3 manual-evidence vocabulary",
        f"and a handful of Annotated/C4 detections differ — **{len(changed)}** repos",
        "change their C1–C4 bitmask):",
        "",
        "| group | v0.4 n | v0.5 n |",
        "|---|---|---|",
    ]
    for g in GROUP_ORDER:
        L.append(f"| {GROUP_LABEL[g]} | {data['v0.4']['group_n'][g]} | "
                 f"{data['v0.5']['group_n'][g]} |")
    L += [f"| **total** | **{n4}** | **{n5}** |", "",
          "## 4. Corpus-level S1–S4", "",
          "| parser | S1 | S2 | S3 | S4 | n |",
          "|---|---|---|---|---|---|",
          dist_row("v0.4 (frozen)", o4, n4),
          dist_row("v0.5 (current)", o5, n5),
          "",
          "The only change v0.4 → v0.5 is the broader S3 vocabulary: it moves",
          f"{o5['S3'] - o4['S3']} repositories into S3 (v0.5 − v0.4: S1 "
          f"{o5['S1'] - o4['S1']:+d}, S2 {o5['S2'] - o4['S2']:+d}, "
          f"S4 {o5['S4'] - o4['S4']:+d}).",
          "",
          "## 5. S1–S4 by ecological group",
          "",
          "### 5.1 v0.5 (current parser, canonical)",
          "",
          "| group | S1 | S2 | S3 | S4 | n |",
          "|---|---|---|---|---|---|",
          ]
    for g in GROUP_ORDER:
        c = Counter(data["v0.5"]["by_group"][g])
        L.append(dist_row(GROUP_LABEL[g], c, data["v0.5"]["group_n"][g]))
    L += [dist_row("corpus", o5, n5, star=True), "",
          "### 5.2 v0.4 (frozen reports, for reference)",
          "",
          "| group | S1 | S2 | S3 | S4 | n |",
          "|---|---|---|---|---|---|",
          ]
    for g in GROUP_ORDER:
        c = Counter(data["v0.4"]["by_group"][g])
        L.append(dist_row(GROUP_LABEL[g], c, data["v0.4"]["group_n"][g]))
    L += [dist_row("corpus", o4, n4, star=True), "",
          "## 6. C1–C4 presence patterns",
          "",
          "| pattern (C1,C2,C3,C4) | meaning | count | share |",
          "|---|---|---|---|",
          ]
    meaning = {"0000": "no C1–C4", "1001": "C1+C4 (`Depends`+yield)",
               "1000": "C1 only (`Depends` only)", "1011": "C1+C3+C4",
               "1010": "C1+C3", "1100": "C1+C2", "1101": "C1+C2+C4",
               "1111": "C1+C2+C3+C4", "1110": "C1+C2+C3", "0100": "C2 only"}
    for pat, c in sorted(data["v0.5"]["by_bits"].items(), key=lambda kv: -kv[1]):
        L.append(f"| {pat} | {meaning.get(pat, '—')} | {c} | {pct(c, n5)} |")
    L += ["", "Pure C3 (0010) and pure C4 (0001) never appear — C3/C4 almost always",
          "co-occur with C1, which is why the ReviewGate benchmark uses the mixed",
          "ecological arms `dy`/`ad`/`ady` rather than forcing pure C3/C4 splits.",
          "",
          "## 7. Reading",
          "",
          "1. **Framework DI dominates whenever present.** Every group that contains a",
          "   core construct (`c1_pure`, `c2_pure`, `dy`, `ad`, `ady`, `other`) is",
          "   ~100% S2. The S1–S4 verdict of a repo is determined by *whether* it uses",
          "   FastAPI DI, not by which spelling.",
          "2. **S3 is residual.** Manual-only S3 occurs almost exclusively in",
          "   `c0_none` (repos with manual wiring but no core construct); v0.5's broader",
          "   S3 vocabulary enlarges exactly this cell.",
          "3. **S4 is thin everywhere** (0.3% corpus-wide; ≤1% per group).",
          "4. **Implication for ReviewGate.** The measured C1–C4 experiment must be read",
          "   as *spelling* effects on the S2 mechanism (all mixed arms are S2), not as",
          "   strategy effects; the strategy story is the S1–S4 Tier-1 benchmark.",
          "",
          "## 8. Known discrepancies across the older ReviewGate notes",
          "",
          "The legacy files (`analysis/syncasync/variants_c1c4/reviewgate_*.md`,",
          "`strategy_simple.md`) disagree because they were produced under different",
          "rules — use **this** document as canonical:",
          "",
          "| file | precedence used | note |",
          "|---|---|---|",
          "| this doc + `docs/s1s4_c1c4_tables.md`, `c1c4_counts.md` | `S4>S2>S3>S1` | canonical |",
          "| `reviewgate_s4s2s1s3.md` | `S4>S2>S1>S3` | hand-set variant (S1 > S3) |",
          "| `reviewgate_summary.md` / `reviewgate_summary_fixed.md` | `S4>S3>S2>S1` | S3 beats S2 → higher S3 shares |",
          "| `summary.md` / `build_c1c4.py` (`c1c4_assignments.csv`) | n/a | *dominance* rule (annotated>yield>security>depends) → c3 384 / c4 533; not the ecological partition |",
          "",
          "## 9. Artifacts",
          "",
          "| artifact | path |",
          "|---|---|",
          "| This computation | `analysis/s1s4_reviewgate_crosswalk.py` |",
          "| Numbers | `analysis/out/s1s4_reviewgate_crosswalk.json` |",
          "| Strategy verdict logic | `extractor/verdict.py` |",
          "| Reports | `corpus/reports_v0.4/`, `corpus/reports_v0.5/` |",
          "| Group lists | `analysis/syncasync/variants_c1c4/*_repos.txt` |",
          "| Design / plan | `analysis/syncasync/variants_c1c4/reviewgate_plan.md`,"
          " `docs/reviewgate_experiment_final.md` |",
          "| Measured C1–C4 run | `docs/c1c4_construct_results.md` |",
          "| Measured S1–S4 run (Tier-1) | `analysis/syncasync/results_5arm_final.md` |",
          "",
          ]
    OUT_MD.write_text("\n".join(L))


if __name__ == "__main__":
    main()
