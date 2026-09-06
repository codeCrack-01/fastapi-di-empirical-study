"""
analysis/pattern_outcomes.py — Phase 2C: observational comparison of DI styles.

Joins pattern_features.csv + ast_quality.csv + github_signals.csv into one
dataset and runs, per outcome, standardized OLS regressions of the outcome on
DI-style predictors controlling for confounding covariates (stars, age, size,
py ratio, tutorial flag). Reports honest effect sizes with 95% CIs (HC1 robust
SEs), NOT a leaderboard of "best pattern".

Likely grill to preempt: these are associative, cross-sectional, proxy outcomes;
Tier-B idiom groups are small (n=1-15) — power is limited; any "which is best"
claim must be bounded. We say so explicitly in the output.

Outputs:
  analysis/out/pattern_outcomes.csv   (joined dataset)
  analysis/out/pattern_compare_results.md
"""

from __future__ import annotations

import csv
import math
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

# (name, transform) for predictors/outcomes where log/spm is sensible
CONTROLS = ["log_stars", "age_months", "py_ratio", "log_loc", "tutorial_flag"]

STYLE_CONTRASTS = [
    ("zero_di", "zero-DI (no DI constructs)"),
    ("uses_class_dep", "class-as-dependency Depends(Class)"),
    ("uses_current", "current_* request-scope injection"),
    ("p_module", "module-alias deps (mod.dep)"),
    ("fanout3", "hub-rich graph (>=3-consumer hub)"),
    ("uses_annotated", "Annotated[...] typed injection"),
]

OUTCOMES = [
    ("hygiene", "engineering-hygiene composite (0..5)", "count"),
    ("sophistication_index", "structural sophistication index", "count"),
    ("mean_func_len", "mean function length (LOC)", "ratio"),
    ("mean_branch_per_func", "mean branch density per function", "ratio"),
    ("docstring_share", "docstring coverage %", "pct"),
    ("type_ann_share", "type-annotation share %", "pct"),
    ("open_issues_ratio", "open issues per 1k LOC", "ratio"),
    ("log_contributors", "log1p(# contributors)", "count"),
]

LOG_OUTCOMES = {"log_contributors"}


def _read(path: str, key: str = "repo") -> dict:
    rows = {}
    with (OUT_DIR / path).open() as fh:
        for r in csv.DictReader(fh):
            rows[r[key]] = r
    return rows


def _log1p(x: float) -> float:
    return math.log1p(max(x, 0.0))


def _join() -> list[dict]:
    feats = _read("pattern_features.csv")
    ast = _read("ast_quality.csv")
    gh = _read("github_signals.csv")
    rows = []
    for repo, f in sorted(feats.items()):
        a = ast.get(repo, {})
        g = gh.get(repo, {})
        loc = float(f.get("py_loc") or 0)
        stars = float(f.get("stars_gh") or 0)
        open_issues = float(g.get("open_issues") or 0)
        size_kb = float(g.get("size_kb") or 0)

        # mutually-exclusive style kind
        if int(f.get("is_zero_di") or 0):
            kind = "zero_di"
        elif int(f.get("uses_class_dep") or 0):
            kind = "class_based"
        elif int(f.get("uses_current") or 0):
            kind = "current_scoped"
        elif float(f.get("p_module") or 0) >= 50:
            kind = "module_alias"
        else:
            kind = "bare_dominant"

        rows.append({
            "repo": repo,
            "kind": kind,
            "zero_di": int(f.get("is_zero_di") or 0),
            "uses_class_dep": int(f.get("uses_class_dep") or 0),
            "uses_current": int(f.get("uses_current") or 0),
            "p_module": float(f.get("p_module") or 0),
            "fanout3": int(f.get("fanout3") or 0),
            "uses_annotated": int(f.get("uses_annotated") or 0),
            "graph_bearing": int(f.get("graph_bearing") or 0),
            # outcomes
            "hygiene": float(f.get("hygiene") or 0),
            "sophistication_index": float(f.get("sophistication_index") or 0),
            "mean_func_len": float(a.get("mean_func_len") or 0),
            "mean_branch_per_func": float(a.get("mean_branch_per_func") or 0),
            "docstring_share": float(a.get("docstring_share") or 0),
            "type_ann_share": float(a.get("type_ann_share") or 0),
            "open_issues_ratio": (open_issues / max(loc, 1) * 1000
                                  if g and g.get("has_issues") != "False" else None),
            "contributors_approx": float(g.get("contributors_approx") or 0),
            "log_contributors": math.log1p(float(g.get("contributors_approx") or 0)),
            # controls
            "log_stars": _log1p(stars),
            "age_months": float(f.get("age_months") or 0),
            "py_ratio": float(f.get("py_ratio") or 0),
            "log_loc": _log1p(loc),
            "tutorial_flag": int(f.get("tutorial_flag") or 0),
            "has_issues": g.get("has_issues") if g else None,
        })
    return rows


def _ols(y: list[float], X: list[list[float]]) -> dict:
    """Standardized beta + HC1 robust SE/CI for OLS (intercept included, then dropped)."""
    n = len(y)
    k = len(X[0])
    # add intercept col
    Xw = [[1.0] + list(row) for row in X]
    # build XtX etc. via loops (pure python)
    p = len(Xw[0])
    XtX = [[0.0] * p for _ in range(p)]
    Xty = [0.0] * p
    for xi, yi in zip(Xw, y):
        for i in range(p):
            Xty[i] += xi[i] * yi
            for j in range(p):
                XtX[i][j] += xi[i] * xi[j]
    # gaussian elimination solve XtX b = Xty
    b = _solve(XtX, Xty)
    # residuals
    rss = 0.0
    for xi, yi in zip(Xw, y):
        pred = sum(b[i] * xi[i] for i in range(p))
        rss += (yi - pred) ** 2
    denom = max(n - p, 1)
    sigma2 = rss / denom
    # covariance via HC1 sandwich
    XtX_inv = _inv(XtX)
    meat = [[0.0] * p for _ in range(p)]
    for xi, r in zip(Xw, [y[i] - sum(b[j] * Xw[i][j] for j in range(p)) for i in range(n)]):
        w = r * r
        for i in range(p):
            for j in range(p):
                meat[i][j] += w * xi[i] * xi[j]
    scale = n / max(n - p, 1)
    cov = [[0.0] * p for _ in range(p)]
    for i in range(p):
        for j in range(p):
            acc = 0.0
            for a in range(p):
                for b2 in range(p):
                    acc += XtX_inv[i][a] * meat[a][b2] * XtX_inv[b2][j]
            cov[i][j] = acc * scale

    rows = []
    for idx in range(1, p):
        beta = b[idx]
        se = math.sqrt(cov[idx][idx]) if cov[idx][idx] > 0 else float("nan")
        lo = beta - 1.96 * se
        hi = beta + 1.96 * se
        rows.append({"beta": beta, "se": se, "ci_lo": lo, "ci_hi": hi,
                     "sig": "**" if (lo > 0 or hi < 0) else ""})
    return {"rows": rows, "n": n, "r2": 1.0 - rss / max(_totss(y), 1e-12)}


def _totss(y: list[float]) -> float:
    m = st.mean(y)
    return sum((v - m) ** 2 for v in y)


def _solve(A: list[list[float]], b: list[float]) -> list[float]:
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        if abs(M[col][col]) < 1e-12:
            continue
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0
    return x


def _inv(A: list[list[float]]) -> list[list[float]]:
    n = len(A)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)]
           for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[piv] = aug[piv], aug[col]
        d = aug[col][col]
        if abs(d) < 1e-12:
            return [[0.0] * n for _ in range(n)]
        for c in range(2 * n):
            aug[col][c] /= d
        for r in range(n):
            if r == col:
                continue
            f = aug[r][col]
            for c in range(col, 2 * n):
                aug[r][c] -= f * aug[col][c]
    return [row[n:] for row in aug]


def _fmt(v: float) -> str:
    if math.isnan(v):
        return "—"
    return f"{v:.3f}"


def main() -> None:
    rows = _join()

    # ---- write joined dataset ----
    cols = list(rows[0].keys())
    with (OUT_DIR / "pattern_outcomes.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    n = len(rows)

    L = []
    L.append("# Pattern comparison — DI styles and maintainability proxies\n")
    L.append(f"- **Sample:** {n} accepted repos; style, AST, and GitHub signals joined. ")
    L.append(f"GitHub issue signals available for "
             f"{sum(1 for r in rows if r.get('has_issues') == 'True')} repos "
             f"({round(100*sum(1 for r in rows if r.get('has_issues') == 'True')/n,1)}%).\n")
    L.append("- **Design & honesty:** cross-sectional, observational, proxy outcomes. ")
    L.append("Standardized OLS (outcome and predictors z-scored) with HC1 robust SEs, ")
    L.append("controlling for stars, age, size, Python share, and tutorial flag. ")
    L.append("Effect sizes and CIs are *associations*, not causal claims; the low-n ")
    L.append("Tier B idiom groups (n=1-15) mean a *ranking* of patterns is not "
             "statistically resolvable here. We report direction/magnitude evidence "
             "only.\n")

    # ---- group-by-style summary ----
    L.append("## Outcome means by DI style\n")
    kinds = ["bare_dominant", "zero_di", "class_based", "current_scoped",
             "module_alias"]
    labels = {"bare_dominant": "bare-function dominant",
              "zero_di": "zero-DI",
              "class_based": "class-as-dependency",
              "current_scoped": "current_* request-scope",
              "module_alias": "module-alias deps"}
    L.append("| style | n | hygiene | sophist. | func_len | branch/fn |"
             " doc% | type-ann% | issues/1kLOC | contribs |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for k in kinds:
        grp = [r for r in rows if r["kind"] == k]
        if not grp:
            continue
        m = lambda kk: _mean_notnone([r[kk] for r in grp])
        L.append(f"| {labels[k]} | {len(grp)} | {m('hygiene'):.2f} | "
                 f"{m('sophistication_index'):.1f} | {m('mean_func_len'):.1f} | "
                 f"{m('mean_branch_per_func'):.2f} | {m('docstring_share'):.0f} | "
                 f"{m('type_ann_share'):.0f} | {m('open_issues_ratio'):.2f} | "
                 f"{m('contributors_approx'):.0f} |")
    L.append("\n")

    # ---- regression tables ----
    for oname, olabel, otype in OUTCOMES:
        model_rows = [r for r in rows if r.get(oname) is not None]
        vals = [r[oname] for r in model_rows]
        mu, sd = st.mean(vals), st.pstdev(vals)
        if sd <= 0 or len(model_rows) < 5:
            continue
        y = [(v - mu) / sd for v in vals]
        # standardize continuous scaled predictors, keep binaries as 0/1
        zcols = {}
        for c in CONTROLS:
            cv = [r[c] for r in model_rows]
            cm, cs = st.mean(cv), st.pstdev(cv)
            zcols[c] = (cm, cs if cs > 1e-12 else 1.0)
        pmod = [r["p_module"] for r in model_rows]
        pm, ps = st.mean(pmod), st.pstdev(pmod)
        zcols["p_module"] = (pm, ps if ps > 1e-12 else 1.0)
        X = []
        for r in model_rows:
            rowv = []
            for c in CONTROLS:
                cm, cs = zcols[c]
                rowv.append((r[c] - cm) / cs)
            for p, _ in STYLE_CONTRASTS:
                if p == "p_module":
                    cm, cs = zcols["p_module"]
                    rowv.append((r[p] - cm) / cs)
                else:
                    rowv.append(float(r[p]))
            X.append(rowv)
        res = _ols(y, X)
        L.append(f"## Outcome: {oname} ({olabel})\n")
        L.append(f"n={res['n']}, R^2={res['r2']:.2f} — standardized beta [95% CI] "
                 "(continuous predictors z-scored; binary predictors 0/1)\n")
        L.append("| predictor | beta | 95% CI |")
        L.append("|---|---|---|")
        for (p, plabel), r in zip(STYLE_CONTRASTS, res["rows"]):
            L.append(f"| {plabel} | {_fmt(r['beta'])} "
                     f"**[{_fmt(r['ci_lo'])}, {_fmt(r['ci_hi'])}]** | "
                     f"{'*sig.*' if r['sig'] else ''}")
        L.append("\n")

    L.append("## Reading (honest)\n")
    L.append("- Any beta whose CI excludes 0 is marked; otherwise direction is "
             "consistent with noise.")
    L.append("- Positive beta = style associated with *higher* outcome. For "
             "func_len/branch density higher = more complex (worse); for doc%/ann% "
             "higher = better; hygiene/contribs higher = healthier.")
    L.append("- Zero-DI and Tier B groups are small: treat their estimates as "
             "evidence-of-direction, not rankings.\n")

    (OUT_DIR / "pattern_compare_results.md").write_text("\n".join(L) + "\n")
    print(f"[pattern_outcomes] joined {n} rows; wrote pattern_outcomes.csv + "
          f"pattern_compare_results.md")


def _mean_notnone(vals) -> float:
    v = [x for x in vals if x is not None]
    return round(st.mean(v), 2) if v else 0.0


def _z(v: float) -> float:
    return float(v)


if __name__ == "__main__":
    main()