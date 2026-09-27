"""analysis/rate_review.py — score the two rated arms.

Reads a finished workbook, reports inter-rater agreement, and for Arm 1
applies the gate that was fixed in docs/audit_preregistration.md before any
rating occurred.

    .venv/bin/python analysis/rate_review.py --arm1
    .venv/bin/python analysis/rate_review.py --arm2b
    .venv/bin/python analysis/rate_review.py --arm1 --arm2b

Handling notes that matter:

* `unclear` is a real answer, so it is never silently dropped. It is counted,
  reported, and excluded from the kappa base with the exclusion stated.
* DISAGREE in the FINAL column means the two raters differ on a row that
  matters; the script lists every one rather than only counting them.
* The Arm 1 gate is applied to the count of reconciled "yes" answers. Rows the
  raters disagreed on are reported separately and never resolved in the
  analyser's favour by default.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "peer_review_kit"

# Column headers carry rater names (see analysis/build_review_workbooks.py).
# Falls back to the abstract A/B names so a pre-rename workbook still scores.
RATER_A = "Zain Ahmed Khan"
RATER_B = "Yahya Ahmed"

ARMS = {
    "arm1": {
        "file": KIT / "AUDIT_80.xlsx",
        "sheet": "audit",
        "options": ("yes", "no", "unclear"),
        "positive": "yes",
        "n": 80,
    },
    "arm2b": {
        "file": KIT / "S3S4_200.xlsx",
        "sheet": "prevalence",
        "options": ("S2", "S3", "S4", "unclear"),
        "positive": None,
        "n": 200,
    },
}

BANDS = [
    (0.81, "almost perfect"),
    (0.61, "substantial"),
    (0.41, "moderate"),
    (0.21, "fair"),
    (0.00, "slight"),
]
GATE = {0: 0.046, 1: 0.067, 2: 0.087, 3: 0.105, 4: 0.122}


def wilson_ci(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Two-sided Wilson score interval. Returns (lower, upper) as fractions."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (centre - margin) / d), (centre + margin) / d)


def wilson_upper(x: int, n: int, z: float = 1.96) -> float:
    return wilson_ci(x, n, z)[1]


def normal_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def cohens_kappa(pairs: list[tuple[str, str]], options: tuple[str, ...]) -> dict:
    """Cohen's kappa over the observed label set (options minus 'unclear')."""
    n = len(pairs)
    labels = [o for o in options if o != "unclear"]
    idx = {l: i for i, l in enumerate(labels)}
    k = len(labels)
    obs = [[0] * k for _ in range(k)]
    for a, b in pairs:
        obs[idx[a]][idx[b]] += 1
    row = [sum(r) for r in obs]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    agree = sum(obs[i][i] for i in range(k)) / n
    exp = sum(row[i] * col[i] for i in range(k)) / (n * n)
    kappa = (agree - exp) / (1 - exp) if exp < 1 else float("nan")
    se = math.sqrt(max(agree * (1 - agree), 1e-12) / n) if kappa == kappa else float("nan")
    z = kappa / se if se else float("nan")
    p = 2 * (1 - normal_cdf(abs(z))) if z == z else float("nan")
    band = next((label for lo, label in BANDS if kappa >= lo), "poor") if kappa == kappa else "?"
    return {
        "n": n, "agree": agree, "expected": exp, "kappa": kappa,
        "z": z, "p": p, "band": band, "labels": labels,
        "matrix": obs, "row": row, "col": col,
    }


def read(path: Path, sheet: str) -> list[dict]:
    wb = load_workbook(path)
    if sheet not in wb.sheetnames:
        raise SystemExit(f"{path.name} has no sheet {sheet!r} (has {wb.sheetnames})")
    ws = wb[sheet]
    hdr = [c.value for c in ws[1]]
    try:
        i_repo = hdr.index("REPO")
        i_a = hdr.index(RATER_A) if RATER_A in hdr else hdr.index("VERDICT_A")
        i_b = hdr.index(RATER_B) if RATER_B in hdr else hdr.index("VERDICT_B")
        # Report whatever the file actually calls them, not the constants.
        name_a, name_b = hdr[i_a], hdr[i_b]
    except ValueError:
        raise SystemExit(
            f"{path.name}/{sheet}: expected REPO plus the rater columns "
            f"{RATER_A!r} and {RATER_B!r} (or VERDICT_A/VERDICT_B). "
            f"Header is: {hdr}"
        )
    rows = []
    for r in range(2, ws.max_row + 1):
        repo = ws.cell(row=r, column=i_repo + 1).value
        if not repo:
            continue
        a = ws.cell(row=r, column=i_a + 1).value
        b = ws.cell(row=r, column=i_b + 1).value
        rows.append({
            "row": r, "repo": repo,
            "a": (a or "").strip() or None,
            "b": (b or "").strip() or None,
        })
    for r in rows:
        r["name_a"], r["name_b"] = name_a, name_b
    return rows


def report(arm: str) -> None:
    cfg = ARMS[arm]
    if not cfg["file"].exists():
        raise SystemExit(f"missing {cfg['file']}")
    rows = read(cfg["file"], cfg["sheet"])
    opts = cfg["options"]
    print(f"\n{'=' * 68}\n{arm.upper()}   {cfg['file'].name}   {len(rows)} rows\n{'=' * 68}")

    blank_a = [r for r in rows if r["a"] is None]
    blank_b = [r for r in rows if r["b"] is None]
    if blank_a or blank_b:
        print(f"  INCOMPLETE: {len(blank_a)} rows missing {rows[0]['name_a']}, "
              f"{len(blank_b)} missing {rows[0]['name_b']}")
        print(f"  first missing rows: "
              f"{[r['row'] for r in (blank_a or blank_b)[:8]]}")
        print("  scoring what is filled in; rerun when both columns are complete.")

    bad = sorted({v for r in rows for v in (r["a"], r["b"])
                  if v is not None and v not in opts})
    if bad:
        print(f"  UNEXPECTED VALUES (not in {list(opts)}): {bad} — these rows are "
              f"excluded from the kappa base")

    only_a = [r for r in rows if r["a"] is not None and r["b"] is None]
    only_b = [r for r in rows if r["b"] is not None and r["a"] is None]
    for r in only_a:
        print(f"  row {r['row']}: A={r['a']} B=<blank>")
    for r in only_b:
        print(f"  row {r['row']}: A=<blank> B={r['b']}")

    pairs = [(r["a"], r["b"]) for r in rows if r["a"] and r["b"]]
    if not pairs:
        print("  no rows rated by both raters yet")
        return
    disagree = [r for r in rows if r["a"] and r["b"] and r["a"] != r["b"]]
    unclear = [r for r in rows if r["a"] and r["b"] and "unclear" in (r["a"], r["b"])]

    print(f"\n  rows rated by both : {len(pairs)}")
    print(f"  exact agreement   : {len(pairs) - len(disagree)}/{len(pairs)} "
          f"({100 * (len(pairs) - len(disagree)) / len(pairs):.1f}%)")
    print(f"  disagreements     : {len(disagree)}")
    print(f"  'unclear' by either rater: {len(unclear)} "
          f"(excluded from kappa, reported here)")

    # The kappa base excludes 'unclear' and any value outside the declared
    # vocabulary. Both exclusions are counted and printed above.
    kappa_base = [(a, b) for a, b in pairs if a in opts and b in opts
                  and "unclear" not in (a, b)]
    kp = cohens_kappa(kappa_base, opts)
    print(f"\n  Cohen's kappa     : {kp['kappa']:.3f}  ({kp['band']})")
    print(f"  observed agreement: {kp['agree']:.3f}   chance: {kp['expected']:.3f}")
    print(f"  n={kp['n']}   z={kp['z']:.2f}   p={kp['p']:.2g}")

    print(f"\n  agreement matrix (rows = {rows[0]['name_a']}, cols = {rows[0]['name_b']})")
    labels = kp["labels"]
    print("      " + "".join(f"{l:>10}" for l in labels) + f"{'total':>10}")
    for i, l in enumerate(labels):
        print(f"  {l:<6}" + "".join(f"{kp['matrix'][i][j]:>10}" for j in range(len(labels)))
              + f"{kp['row'][i]:>10}")
    print(f"  {'total':<6}" + "".join(f"{c:>10}" for c in kp["col"]))

    if disagree:
        print(f"\n  disagreements ({len(disagree)}):")
        for r in disagree[:40]:
            print(f"    row {r['row']:<4} {r['repo']:<44} {r['name_a']}={r['a']:<8} {r['name_b']}={r['b']}")
        if len(disagree) > 40:
            print(f"    ... and {len(disagree) - 40} more")

    if cfg["positive"]:
        pos = cfg["positive"]
        agreed = [r for r in rows if r["a"] == r["b"] == pos]
        one = [r for r in rows if r["a"] != r["b"] and pos in (r["a"], r["b"])]
        unres = len(one)
        print(f"\n  --- ARM 1 GATE ---")
        print(f"  agreed '{pos}' (misses)   : {len(agreed)}")
        print(f"  disagreements involving '{pos}': {unres} "
              f"(unresolved — the gate is not applied to them automatically)")
        for r in one:
            print(f"    row {r['row']:<4} {r['repo']:<44} {r['name_a']}={r['a']:<8} {r['name_b']}={r['b']}")
        k = len(agreed)
        ub = wilson_upper(k, len(rows))
        print(f"\n  k = {k} of {len(rows)}   95% Wilson upper bound = {100 * ub:.1f}%")
        if unres:
            print("  GATE: cannot be applied until the above are adjudicated.")
        elif k >= 4:
            print("  GATE: >= 4 misses  ->  STOP. No headline number. Extend the extractor.")
        elif k >= 2:
            print("  GATE: 2-3 misses  ->  proceed, but report the zero-DI share as a RANGE.")
        else:
            print("  GATE: 0-1 misses  ->  proceed; the upper bound is reportable as it stands.")
        print(f"  reference bounds: " + "  ".join(
            f"{i}:{100 * v:.1f}%" for i, v in GATE.items()))
    else:
        s3 = [r for r in rows if r["a"] == r["b"] == "S3"]
        s4 = [r for r in rows if r["a"] == r["b"] == "S4"]
        non = [r for r in rows if r["a"] == r["b"] and r["a"] in ("S3", "S4")]
        n = len([r for r in rows if r["a"] and r["b"] and "unclear" not in (r["a"], r["b"])])
        if n:
            k = len(non)
            lo, hi = wilson_ci(k, n)
            print(f"\n  --- ARM 2b PREVALENCE ---")
            print(f"  denominator (rows rated by both, no 'unclear') : {n}")
            print(f"  agreed S3 : {len(s3)}   agreed S4 : {len(s4)}")
            print(f"  S3 or S4  : {k}/{n} = {100 * k / n:.1f}%  "
                  f"95% Wilson CI [{100 * lo:.1f}%, {100 * hi:.1f}%]")
            if k:
                lo0, hi0 = wilson_ci(0, n)
                print(f"  zero-count bound: if the true count were 0, the 95% upper "
                      f"bound is {100 * hi0:.1f}%")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--arm1", action="store_true")
    g.add_argument("--arm2b", action="store_true")
    g.add_argument("--arm2a", action="store_true")
    a = ap.parse_args()
    if a.arm1:
        report("arm1")
    if a.arm2b:
        report("arm2b")
    if a.arm2a:
        p = KIT / "S3S4_CANDIDATES.xlsx"
        if not p.exists():
            raise SystemExit(f"missing {p}")
        ws = load_workbook(p)["candidates"]
        hdr = [c.value for c in ws[1]]
        i_is = hdr.index("IS THIS DI?") + 1
        i_m = hdr.index("MECHANISM") + 1
        rows = [r for r in range(2, ws.max_row + 1) if ws.cell(row=r, column=2).value]
        done = [r for r in rows if ws.cell(row=r, column=i_is).value]
        print(f"\nARM 2A   S3S4_CANDIDATES.xlsx   {len(done)}/{len(rows)} rows completed")
        if done:
            from collections import Counter
            mech = Counter(ws.cell(row=r, column=i_m).value or "(blank)" for r in done)
            isdi = Counter(ws.cell(row=r, column=i_is).value or "(blank)" for r in done)
            print("  MECHANISM:")
            for k, v in mech.most_common():
                print(f"    {v:>3}  {k}")
            print("  IS THIS DI?")
            for k, v in isdi.most_common():
                print(f"    {v:>3}  {k}")
            print("  (no kappa for this arm by design; it is rubric development)")


if __name__ == "__main__":
    main()
