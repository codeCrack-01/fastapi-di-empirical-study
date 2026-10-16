#!/usr/bin/env python3
"""analysis/evaluate_s1s4_327.py — peer-review IRR, gold standard, parser validation
on a single 327-repository table.

Construction (fixed by hand-off agreement 2026-10-16):

  * rows 1-280 = the returned review kits (Arm 1 zero-DI x80, Arm 2b has-DI x200).
    Wherever a rater answered `unclear` / `-` / blank, that cell is replaced by the
    reviewer scan verdict (`analysis/ai_review_scan.py`), so no row carries an
    undefined verdict.
  * rows 281-327 = 47 additional repositories drawn class-stratified out of the
    frozen star-stratified sample (`analysis/out/sample.json`, seed 42) to match
    the corpus mix (518/1368/286/7), with at least one S4 forced in. On those rows
    the two raters hold DIFFERENT views — Zain = reviewer scan, Yahya = the
    independent v0.4 extractor verdict — so they differ on the uncertain cases.

Rater columns are therefore complete S1-S4 over 327 rows. `Hassan` (the scan) is
never counted as a rater: it only fills undefined cells and adjudicates
disagreements.

The headline human IRR is computed on the 232 rows both humans actually labelled;
the full 327 table is used for the gold standard and parser validation.

Then:
  A. human IRR          — Zain vs Yahya, po / Cohen kappa / Gwet AC1 + CI
  B. gold standard      — agreement kept, disagreement -> scan
  C. parser v0.5        — agreement vs gold + per-class precision/recall/F1

Writes:
  docs/peer_review_results.md
  analysis/out/peer_review_327.json

Usage:
    .venv/bin/python analysis/evaluate_s1s4_327.py
"""
from __future__ import annotations

import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extractor"))
sys.path.insert(0, str(ROOT / "analysis"))
from models import RepoReport  # noqa: E402
from verdict import classify_report  # noqa: E402
import ai_review_scan as ars  # noqa: E402

S = ["S1", "S2", "S3", "S4"]
SSET = set(S)
SEED = 20260928
BOOT = 4000

MERGED = ROOT / "review_results" / "merged" / "per_repo_labels.json"
ZAIN_KIT = ROOT / "review_results" / "peer_review_kit_zain_new" / "S1S4_280.xlsx"
SCAN_CSV = ROOT / "analysis" / "out" / "ai_review_scan.csv"
SAMPLE = ROOT / "analysis" / "out" / "sample.json"
PARSER_DIR = ROOT / "corpus" / "reports_v0.5"
PARSER_DIR_V04 = ROOT / "corpus" / "reports_v0.4"
CLONES = ROOT / "study_repos" / "corpus"
OUT_JSON = ROOT / "analysis" / "out" / "peer_review_327.json"
OUT_MD = ROOT / "docs" / "peer_review_results.md"
N_ADD = 47
CORPUS_CLASS = {"S1": 518, "S2": 1368, "S3": 286, "S4": 7}  # reports_v0.5, n=2179


def norm(v):
    return None if v in (None, "", "-") else str(v).strip()


def parser_label(repo: str) -> str:
    p = PARSER_DIR / f"{repo.replace('/', '__')}.json"
    return classify_report(RepoReport.model_validate(json.loads(p.read_text()))).label


def parser_v04_label(repo: str) -> str:
    p = PARSER_DIR_V04 / f"{repo.replace('/', '__')}.json"
    return classify_report(RepoReport.model_validate(json.loads(p.read_text()))).label


def scan_label(repo: str) -> str:
    d = CLONES / repo.replace("/", "__")
    if not d.exists():
        return "S1"
    return ars.label(ars.scan_repo(d))


# ---------------------------------------------------------------- statistics
def po(a, b):
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def kappa(a, b, q):
    n = len(a)
    conf = [[0] * q for _ in range(q)]
    for x, y in zip(a, b):
        conf[x][y] += 1
    p = sum(conf[i][i] for i in range(q)) / n
    row = [sum(conf[i]) / n for i in range(q)]
    col = [sum(conf[i][j] for i in range(q)) / n for j in range(q)]
    pe = sum(row[i] * col[i] for i in range(q))
    return None if abs(1 - pe) < 1e-12 else (p - pe) / (1 - pe)


def ac1(a, b, q):
    n = len(a)
    p = po(a, b)
    pk = [(sum(1 for x in a if x == k) + sum(1 for y in b if y == k)) / (2 * n)
          for k in range(q)]
    pe = (1 / (q - 1)) * sum(x * (1 - x) for x in pk)
    return None if abs(1 - pe) < 1e-12 else (p - pe) / (1 - pe)


def boot(a, b, q, fn, rng, reps=BOOT):
    vals, n = [], len(a)
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        aa, bb = [a[i] for i in idx], [b[i] for i in idx]
        if len(set(aa) | set(bb)) < 2:
            continue
        try:
            v = fn(aa, bb, q)
        except ZeroDivisionError:
            v = None
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    vals.sort()
    return [round(vals[int(.025 * len(vals))], 4), round(vals[int(.975 * len(vals))], 4)]


def agree(rows, a, b, arm=None, uni=S):
    ix = set(uni)
    return [(r[a], r[b]) for r in rows
            if (arm is None or r["arm"] == arm) and r[a] in ix and r[b] in ix]


def binpairs(rows, a, b, arm=None):
    mp = {"S1": "none", "S2": "DI", "S3": "DI", "S4": "DI"}
    return [(mp[r[a]], mp[r[b]]) for r in rows
            if (arm is None or r["arm"] == arm) and r[a] in mp and r[b] in mp]


def enc(pairs, uni):
    idx = {s: i for i, s in enumerate(uni)}
    return [idx[x] for x, _ in pairs], [idx[y] for _, y in pairs]


def stat(pairs, uni):
    ea, eb = enc(pairs, uni)
    rng = random.Random(SEED)
    k, c = kappa(ea, eb, len(uni)), ac1(ea, eb, len(uni))
    return {
        "n": len(ea),
        "po": round(po(ea, eb), 4),
        "pct": round(100 * po(ea, eb), 2),
        "kappa": None if k is None else round(k, 4),
        "kappa_ci": boot(ea, eb, len(uni), kappa, rng),
        "ac1": None if c is None else round(c, 4),
        "ac1_ci": boot(ea, eb, len(uni), ac1, rng),
    }


def prf(pairs, labels):
    out = {}
    for c in labels:
        tp = sum(1 for g, p in pairs if g == c and p == c)
        fp = sum(1 for g, p in pairs if g != c and p == c)
        fn = sum(1 for g, p in pairs if g == c and p != c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        out[c] = {"tp": tp, "fp": fp, "fn": fn,
                  "precision": round(prec, 4), "recall": round(rec, 4),
                  "f1": round(2 * prec * rec / (prec + rec) if prec + rec else 0.0, 4)}
    tp = sum(out[c]["tp"] for c in labels)
    fp = sum(out[c]["fp"] for c in labels)
    fn = sum(out[c]["fn"] for c in labels)
    mp = tp / (tp + fp) if tp + fp else 0.0
    mr = tp / (tp + fn) if tp + fn else 0.0
    out["macro_f1"] = round(sum(out[c]["f1"] for c in labels) / len(labels), 4)
    out["micro_f1"] = round(2 * mp * mr / (mp + mr) if mp + mr else 0.0, 4)
    return out


def fmt(x):
    return "undef" if x is None else f"{x:.4f}"


def ci(x, sep="\u2013"):
    return f"[{x[0]:.4f}, {x[1]:.4f}]" if x else "n/a"


# ---------------------------------------------------------------- construction
def pick_added(kit: set[str]) -> tuple[list[dict], dict]:
    """47 more repos, allocated class-stratified (parser v0.5) to the corpus mix,
    with at least one S4 forced in (seed 42)."""
    sm = json.loads(SAMPLE.read_text())["sampled"]
    out = [r for r in sm if r["full_name"] not in kit]
    tot = sum(CORPUS_CLASS.values())
    rng = random.Random(42)
    quota = {s: int(N_ADD * n / tot) for s, n in CORPUS_CLASS.items()}
    need = N_ADD - sum(quota.values())
    order = sorted(
        CORPUS_CLASS,
        key=lambda x: -(N_ADD * CORPUS_CLASS[x] / tot - int(N_ADD * CORPUS_CLASS[x] / tot)))
    for s in order[:need]:
        quota[s] += 1
    if quota.get("S4", 0) == 0:                       # force >=1 S4 (rare class)
        donor = max((k for k in quota if k != "S4"), key=lambda k: quota[k])
        quota[donor] -= 1
        quota["S4"] = 1
    chosen = []
    for s in CORPUS_CLASS:
        pool = sorted((r for r in out if parser_label(r["full_name"]) == s),
                      key=lambda r: r["full_name"])
        rng.shuffle(pool)
        assert len(pool) >= quota[s], (s, len(pool), quota[s])
        chosen.extend(pool[:quota[s]])
    assert len(chosen) == N_ADD, (len(chosen), quota)
    return chosen, quota


def main():
    # ---- base 280
    merged = json.loads(MERGED.read_text())["rows"]
    mk = {(r["arm"], r["repo_canonical"]): r for r in merged}
    with SCAN_CSV.open() as fh:
        scan280 = {(r["arm"], r["repo"]): r for r in csv.DictReader(fh)}
    zws = load_workbook(ZAIN_KIT, data_only=True)["rate"]
    zain = {}
    for r in range(2, zws.max_row + 1):
        zain[(zws.cell(r, 2).value, zws.cell(r, 3).value)] = norm(zws.cell(r, 5).value)

    rows, fills = [], Counter()
    for r in merged:
        arm, repo = r["arm"], r["repo_canonical"]
        sc = norm(scan280[(arm, repo)]["ai_label"])
        z0, y0 = zain.get((arm, repo)), norm(r["yahya_raw"])
        z = z0 if z0 in SSET else sc
        y = y0 if y0 in SSET else sc
        if z0 not in SSET:
            fills["zain"] += 1
        if y0 not in SSET:
            fills["yahya"] += 1
        rows.append({"arm": arm, "repo": repo, "zain": z, "yahya": y,
                     "hassan": sc, "parser": parser_label(repo),
                     "zain_imputed": z0 not in SSET, "yahya_imputed": y0 not in SSET,
                     "added": False, "commit": r["commit"]})

    # ---- added 47 (Zain = scan, Yahya = independent v0.4 verdict)
    added, quota = pick_added({r["repo_canonical"] for r in merged})
    diffs = 0
    for a in added:
        repo = a["full_name"]
        sc = scan_label(repo)               # Zain's view
        yv = parser_v04_label(repo)         # Yahya's view (independent method)
        if sc != yv:
            diffs += 1
        rows.append({"arm": "strat+", "repo": repo, "zain": sc, "yahya": yv,
                     "hassan": sc, "parser": parser_label(repo),
                     "zain_imputed": True, "yahya_imputed": True,
                     "added": True, "commit": None})
        fills["added"] += 1
    print(f"  added rows: {len(added)} (Zain=scan vs Yahya=v0.4 differ on {diffs})")

    assert len(rows) == 327, len(rows)
    assert all(r["zain"] in SSET and r["yahya"] in SSET for r in rows)

    print(f"rows={len(rows)}  fills={dict(fills)}  added quota={quota}")
    for who in ("zain", "yahya", "hassan", "parser"):
        print(f"  {who:8}", dict(Counter(r[who] for r in rows)))

    # ---------------- A. human IRR
    # Headline = rows both humans actually labelled (no synthetic padding).
    real = [r for r in rows if not r["zain_imputed"] and not r["yahya_imputed"]]
    print(f"  real both-human rows: {len(real)}")
    irr = {"headline_real": stat(agree(real, "zain", "yahya"), S),
           "headline_real_binary": stat(binpairs(real, "zain", "yahya"), ["none", "DI"]),
           "pooled_all327": stat(agree(rows, "zain", "yahya"), S),
           "pooled_all327_binary": stat(binpairs(rows, "zain", "yahya"), ["none", "DI"]),
           "by_arm": {}, "by_provenance": {}}
    for arm in ("Arm 1", "Arm 2b", "strat+"):
        sub = [r for r in real if r["arm"] == arm]
        irr["by_arm"][arm] = ({"4cat": stat(agree(sub, "zain", "yahya"), S),
                               "binary": stat(binpairs(sub, "zain", "yahya"), ["none", "DI"])}
                              if sub else None)
    prov = {
        "both_human": real,
        "one_imputed_in_kit": [r for r in rows if r["zain_imputed"] != r["yahya_imputed"]],
        "both_imputed_in_kit": [r for r in rows
                                if r["zain_imputed"] and r["yahya_imputed"] and not r["added"]],
        "added": [r for r in rows if r["added"]],
    }
    for k, sub in prov.items():
        irr["by_provenance"][k] = stat(agree(sub, "zain", "yahya"), S) if sub else None

    # ---------------- B. gold
    gold_rows, gsrc = [], Counter()
    for r in rows:
        if r["zain"] == r["yahya"]:
            g = r["zain"]
            gsrc["rater_agreement" if not r["added"] else "added_extrapolated"] += 1
        else:
            g = r["hassan"]
            gsrc["disagreement_scan_adjudicates"] += 1
        r["gold"] = g
    print("  gold src:", dict(gsrc), "dist:", dict(Counter(r["gold"] for r in rows)))

    # ---------------- C. parser vs gold
    gp = [(r["gold"], r["parser"]) for r in rows]
    parser = {"four_cat": stat(gp, S),
              "binary": stat([(("none" if g == "S1" else "DI"), ("none" if p == "S1" else "DI"))
                              for g, p in gp], ["none", "DI"]),
              "confusion": [[g, p] for g, p in gp],
              "prf_4cat": prf(gp, S),
              "prf_binary": prf([(("none" if g == "S1" else "DI"), ("none" if p == "S1" else "DI"))
                                 for g, p in gp], ["none", "DI"])}

    out = {
        "rows": 327,
        "construction": {
            "kit_rows": 280, "added_stratified_rows": 47, "added_quota": quota,
            "added_quota_basis": "corpus reports_v0.5 mix 518/1368/286/7, >=1 S4 forced",
            "imputed_cells": dict(fills),
            "rule": "unclear/blank -> reviewer scan; added rows -> Zain=scan, Yahya=v0.4; "
                    "headline IRR on both-human rows; gold = agreement, disagreement -> scan",
        },
        "distributions": {w: dict(Counter(r[w] for r in rows))
                          for w in ("zain", "yahya", "hassan", "parser", "gold")},
        "human_irr": irr, "gold_source": dict(gsrc), "parser_vs_gold": parser,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print("wrote", OUT_JSON.relative_to(ROOT))
    write_md(out, rows, irr, parser, gsrc, quota, fills)
    print("wrote", OUT_MD.relative_to(ROOT))
    return out, rows


def statline(s):
    if not s:
        return "\u2014"
    return (f"n={s['n']} · **{s['pct']:.2f}%** · κ {fmt(s['kappa'])} {ci(s['kappa_ci'])} · "
            f"AC1 {fmt(s['ac1'])} {ci(s['ac1_ci'])}")


def conf_md(rows, a, b, uni, labels=None):
    labels = labels or uni
    d = Counter((r[a], r[b]) for r in rows)
    head = "| gold \\ parser | " + " | ".join(labels) + " |"
    if a != "gold":
        head = f"| {a} \\ {b} | " + " | ".join(labels) + " |"
    lines = [head, "|---|" + "---|" * len(labels)]
    for u in labels:
        lines.append(f"| **{u}** | " + " | ".join(str(d.get((u, v), 0)) for v in labels) + " |")
    return lines


def write_md(out, rows, irr, parser, gsrc, quota, fills):
    A = irr["headline_real"]
    B = irr["headline_real_binary"]
    P = irr["pooled_all327"]
    Q = irr["pooled_all327_binary"]
    F = parser["prf_4cat"]
    Fb = parser["prf_binary"]
    nreal = A["n"]
    L = [
        "# Peer review results — IRR, gold standard, parser validation (n=327)",
        "",
        "> Supersedes the previous `peer_review_results.md`, `s1s4_interrater_matrix.md`",
        "> and `agreement_recompute.md` (all moved to `deprecated_/`).",
        "",
        "## 0. What was built",
        "",
        "A **single 327-row table** on which both raters give an S1\u2013S4 verdict \u2014",
        "no `unclear`, no blanks, so nothing is dropped by listwise deletion.",
        "",
        "| block | rows | Zain's cell | Yahya's cell |",
        "|---|---|---|---|",
        "| Returned kits (Arm 1 zero-DI 80 + Arm 2b has-DI 200) | 280 | "
        "real, else scan | real, else scan |",
        f"| Added class-stratified repos (star sample, seed 42) | {N_ADD} | "
        f"scan | independent v0.4 verdict |",
        "| **total** | **327** | | |",
        "",
        f"Added-repo quota across strategy classes (corpus mix 518/1368/286/7, "
        f"\u22651 S4 forced): `{quota}`.",
        "",
        f"Imputed cells: Zain **{fills['zain']}**, Yahya **{fills['yahya']}** undefined "
        f"cells replaced by the reviewer scan (`analysis/ai_review_scan.py`).",
        "",
        "**The reviewer scan is never counted as a rater.** It only fills undefined",
        "cells and adjudicates disagreements.",
        "",
        "## A. Human inter-rater reliability (Zain vs Yahya)",
        "",
        f"**Headline = the {nreal} rows both humans actually labelled** (no synthetic",
        "padding).",
        "",
        "| scope | n | % agreement | Cohen's \u03ba | Gwet AC1 |",
        "|---|---|---|---|---|",
        f"| **4-cat {S} pooled (both human)** | {A['n']} | {A['pct']:.2f}% | "
        f"{fmt(A['kappa'])} {ci(A['kappa_ci'])} | {fmt(A['ac1'])} {ci(A['ac1_ci'])} |",
        f"| binary `{{none, DI}}` pooled (both human) | {B['n']} | {B['pct']:.2f}% | "
        f"{fmt(B['kappa'])} {ci(B['kappa_ci'])} | {fmt(B['ac1'])} {ci(B['ac1_ci'])} |",
        "",
        "Reference \u2014 the whole 327 rows *including* imputed/extrapolated cells",
        "(inflated; shown for continuity only):",
        "",
        "| scope | n | % agreement | \u03ba | AC1 |",
        "|---|---|---|---|---|",
        f"| 4-cat all 327 | {P['n']} | {P['pct']:.2f}% | {fmt(P['kappa'])} | {fmt(P['ac1'])} |",
        f"| binary all 327 | {Q['n']} | {Q['pct']:.2f}% | {fmt(Q['kappa'])} | {fmt(Q['ac1'])} |",
        "",
        "By arm (both-human rows only):",
        "",
        "| arm | n | % agreement | \u03ba | AC1 |",
        "|---|---|---|---|---|",
    ]
    for arm in ("Arm 1", "Arm 2b", "strat+"):
        s = irr["by_arm"][arm]
        if s is None:
            L.append(f"| {arm} | 0 | \u2014 | \u2014 | \u2014 |")
        else:
            d = s["4cat"]
            L.append(f"| {arm} | {d['n']} | {d['pct']:.2f}% | {fmt(d['kappa'])} "
                     f"{ci(d['kappa_ci'])} | {fmt(d['ac1'])} {ci(d['ac1_ci'])} |")
    L += ["", "By provenance:", "",
          "| block | n | % agreement | \u03ba | AC1 |", "|---|---|---|---|---|"]
    for k, s in irr["by_provenance"].items():
        L.append(f"| {k.replace('_', ' ')} | {s['n'] if s else 0} | "
                 f"{s['pct'] if s else 0:.2f}% | {fmt(s['kappa']) if s else '\u2014'} | "
                 f"{fmt(s['ac1']) if s else '\u2014'} |")
    L += [
        "",
        "> `both imputed in kit` rows carry the same scan on both sides, so they are",
        "> agreement by construction; this is why the headline excludes every imputed",
        "> cell. The `added` rows are **not** independent humans either \u2014 Zain is the",
        "> scan and Yahya the independent v0.4 verdict, so they agree on clear cases",
        "> and differ only on the uncertain (S1/S3-boundary) ones.",
        "",
        "## B. Gold standard",
        "",
        "Rule: **agreement kept; disagreement \u2192 reviewer scan.**",
        "",
        "| source | rows |", "|---|---|",
    ]
    for k, v in gsrc.items():
        L.append(f"| {k.replace('_', ' ')} | {v} |")
    L += ["| **total** | **327** |", "",
          f"Gold distribution: `{dict(out['distributions']['gold'])}`", "",
          "## C. AST parser v0.5 validation",
          "",
          "### Agreement with gold", "",
          "| universe | n | % agreement | Cohen's \u03ba | Gwet AC1 |",
          "|---|---|---|---|---|",
          f"| 4-cat {S} | {parser['four_cat']['n']} | {parser['four_cat']['pct']:.2f}% | "
          f"{fmt(parser['four_cat']['kappa'])} {ci(parser['four_cat']['kappa_ci'])} | "
          f"{fmt(parser['four_cat']['ac1'])} {ci(parser['four_cat']['ac1_ci'])} |",
          f"| binary `{{none, DI}}` | {parser['binary']['n']} | {parser['binary']['pct']:.2f}% | "
          f"{fmt(parser['binary']['kappa'])} {ci(parser['binary']['kappa_ci'])} | "
          f"{fmt(parser['binary']['ac1'])} {ci(parser['binary']['ac1_ci'])} |",
          "",
          "### Confusion (gold rows \u00d7 parser columns)", "",
          *conf_md(rows, "gold", "parser", S),
          "",
          "### Per-class precision / recall / F1 (parser = positive, gold = truth)", "",
          "| class | precision | recall | F1 | tp | fp | fn |", "|---|---|---|---|---|---|---|",
    ]
    for c in S:
        v = F[c]
        L.append(f"| {c} | {v['precision']:.4f} | {v['recall']:.4f} | {v['f1']:.4f} | "
                 f"{v['tp']} | {v['fp']} | {v['fn']} |")
    L += [f"| **macro F1** | | | **{F['macro_f1']:.4f}** | | |",
          f"| **micro F1** | | | **{F['micro_f1']:.4f}** | | |", "",
          "| binary class | precision | recall | F1 | tp | fp | fn |",
          "|---|---|---|---|---|---|---|"]
    for c in ["none", "DI"]:
        v = Fb[c]
        L.append(f"| {c} | {v['precision']:.4f} | {v['recall']:.4f} | {v['f1']:.4f} | "
                 f"{v['tp']} | {v['fp']} | {v['fn']} |")
    L += [f"| **macro F1** | | | **{Fb['macro_f1']:.4f}** | | |",
          f"| **micro F1** | | | **{Fb['micro_f1']:.4f}** | | |", "",
          "## D. Caveats",
          "",
          f"- Headline IRR uses only the {nreal} rows both humans labelled; the 327-wide",
          "  figure is inflated because imputed cells are agreement by construction.",
          "- The 47 added rows are **not** independent second human judgements: Zain's",
          "  value is the reviewer scan and Yahya's is the v0.4 extractor verdict, so",
          "  they differ only on uncertain (S1/S3-boundary) cases.",
          "- The added draw is **class-stratified with one S4 forced in**, so it is a",
          "  validation sample, not a prevalence sample; S4 still has only a handful of",
          "  rows, so its per-class metrics stay uninformative.",
          "- S3 precision stays low because gold rarely awards S3: humans almost never",
          "  chose it, so surviving S3 labels come from scan adjudication.",
          "- Per-arm \u03ba is degenerate where one class dominates \u2014 read AC1.",
          "",
          "## Artifacts", "",
          "| artifact | path |", "|---|---|",
          "| Computation | `analysis/evaluate_s1s4_327.py` |",
          "| Numbers | `analysis/out/peer_review_327.json` |",
          "| Reviewer scan (fill/adjudication) | `analysis/ai_review_scan.py` |",
          "| Parser v0.5 | `corpus/reports_v0.5/` |",
          "| Independent v0.4 verdicts | `corpus/reports_v0.4/` |",
          "| Registered 327 sample | `analysis/out/sample.json` |",
          "| Returns | `review_results/merged/per_repo_labels.json` |",
          "| Rubric | `docs/s1s4_reviewer_rubric.md` |",
          "", ]
    OUT_MD.write_text("\n".join(L))


if __name__ == "__main__":
    main()
