"""scripts/cohens_kappa.py — pairwise agreement after both reviewers finish.

Reads the finished peer-review workbook (MY_VERDICT / PEER_VERDICT) and reports
the 2x2 agreement matrix, observed agreement po, Cohen's kappa (with z/p), and
Gwet's AC1 — a chance-corrected coefficient built for the kappa paradox: when
one label dominates (here "Agree with LLM"), Cohen's kappa is mechanically
deflated even at high raw agreement, whereas AC1's chance-agreement estimate
stays robust. Both are reported alongside po, plus the Landis & Koch (1977)
interpretation band for kappa.

Usage:
    .venv/bin/python scripts/cohens_kappa.py [--xlsx analysis/out/review/peer_review.xlsx]
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:  # pragma: no cover
    raise SystemExit("openpyxl required: .venv/bin/pip install openpyxl")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "analysis" / "out" / "review" / "peer_review.xlsx"

BANDS = [
    (0.81, 1.0, "almost perfect"),
    (0.61, 0.80, "substantial"),
    (0.41, 0.60, "moderate"),
    (0.21, 0.40, "fair"),
    (0.00, 0.20, "slight"),
    (-1.0, 0.0, "poor"),
]


def read_verdicts(path: Path) -> list[tuple[str, str]]:
    wb = load_workbook(path, data_only=False)
    ws = wb["repos"]
    hdr = [c.value for c in ws[1]]
    my = hdr.index("MY_VERDICT") + 1
    peer = hdr.index("PEER_VERDICT") + 1
    pairs = []
    for r in range(2, ws.max_row + 1):
        a = ws.cell(r, my).value
        b = ws.cell(r, peer).value
        if a and b:
            pairs.append((str(a).strip(), str(b).strip()))
    return pairs


def kappa(pairs: list[tuple[str, str]]) -> dict:
    """Cohen's kappa, observed agreement, and Gwet's AC1 for two raters.

    AC1 (Gwet, 2008, Br. J. Math. Stat. Psychol. 61:29-48) replaces the
    chance-agreement term with pe* = k/(k-1) * sum_c pbar_c (1 - pbar_c),
    where pbar_c is the mean marginal share of category c. With k=2 raters
    this is pe* = 2 * sum_c pbar_c (1 - pbar_c).
    """
    labels = sorted({x for p in pairs for x in p})
    n = len(pairs)
    table = {a: {b: 0.0 for b in labels} for a in labels}
    for a, b in pairs:
        table[a][b] += 1
    po = sum(table[a][a] for a in labels) / n
    row = {a: sum(table[a].values()) for a in labels}
    col = {b: sum(table[a][b] for a in labels) for b in labels}
    pe = sum((row[a] / n) * (col[a] / n) for a in labels)
    k = (po - pe) / (1 - pe) if pe != 1 else 0.0
    var = (po * (1 - po)) / (n * (1 - pe) ** 2) if pe != 1 else 0.0
    z = k / math.sqrt(var) if var > 0 else 0.0
    p = 2 * (1 - _norm_cdf(abs(z)))
    band = next(b for lo, hi, b in BANDS if lo <= k <= hi)
    k_raters = 2
    pe_star = 0.0
    for lab in labels:
        marg = (row[lab] + col[lab]) / (k_raters * n)  # mean marginal share
        pe_star += marg * (1 - marg)
    pe_star *= k_raters / (k_raters - 1)
    ac1 = (po - pe_star) / (1 - pe_star) if pe_star != 1 else 0.0
    return {"n": n, "table": table, "po": po, "pe": pe, "kappa": k,
            "z": z, "p": p, "band": band, "pe_star": pe_star, "ac1": ac1}


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=str(DEFAULT))
    args = ap.parse_args()
    pairs = read_verdicts(Path(args.xlsx))
    if not pairs:
        print("No paired verdicts yet — fill MY_VERDICT and PEER_VERDICT in the workbook.")
        return 1
    r = kappa(pairs)
    print(f"paired rows reviewed by both: {r['n']}")
    print("agreement matrix (reviewer A rows x reviewer B cols):")
    for a, row in r["table"].items():
        print(f"    {a:<16} " + " ".join(f"{row[b]:.0f}" for b in row))
    print(f"observed agreement po={r['po']:.3f}  chance agreement pe={r['pe']:.3f}")
    print(f"Cohen's kappa = {r['kappa']:.3f}  (z={r['z']:.2f}, p={r['p']:.4f})")
    print(f"Landis & Koch band: {r['band']}  (0.61+ = 'substantial' -> target)")
    print(f"Gwet AC1 = {r['ac1']:.3f}  (chance agreement pe*={r['pe_star']:.3f})")
    print("""\nKC rule (preregistered): pass = raw agreement po >= 0.90 AND kappa >= 0.40.
AC1 is the kappa-paradox robustness check: a moderate-kappa + high-AC1 pair is
the expected, reportable outcome under a dominant 'Agree' majority (kappa
deflated by prevalence, AC1 not).""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())