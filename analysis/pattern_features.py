"""
analysis/pattern_features.py — Phase 1: per-repo DI-pattern feature matrix.

Joins, for every accepted repo, a predictor vector describing *how* it uses
FastAPI DI (style) plus graph topology plus confounders. Consumes only the
frozen corpus/analysis outputs (no network, no re-extraction):

  corpus/manifest.json
  corpus/reports/*.json
  analysis/out/rq1_constructs.csv        (per-repo uses not here — but aggregate)
  analysis/out/usage_patterns.csv        (corpus-level; NOT per-repo)
  analysis/out/rq4_graphs.csv            (per-repo graph topology)
  analysis/out/covariates.csv            (stars/age/dates/tutorial_flag)
  analysis/out/e6_structural.csv         (sophistication, hygiene booleans)

Note: usage_patterns.csv is corpus-aggregated, so per-repo style predictors are
recomputed here from the reports (the same computations usage_patterns.py does,
but kept per-repo): argument-shape shares, class/current/module-alias usage,
class-node ratio, unresolved flag, fan-out presence.

Output: analysis/out/pattern_features.csv (one row per accepted repo).
"""  # noqa: D205

from __future__ import annotations

import csv
import json
import re
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
REPORTS_DIR = ROOT.parent / "corpus" / "reports"
MANIFEST = ROOT.parent / "corpus" / "manifest.json"

TITLE_CLASS = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
DOTTED_CLASSMETHOD = re.compile(r"^[A-Z][A-Za-z0-9_]*\.[a-z_][A-Za-z0-9_]*$")
DOTTED = re.compile(r"^[a-z_][A-Za-z0-9_]*(\.[a-z_][A-Za-z0-9_]*)+$")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _load() -> dict[str, dict]:
    manifest = json.loads(MANIFEST.read_text())
    accepted = [a["full_name"] for a in manifest["accepted"]]
    out = {}
    for name in accepted:
        p = REPORTS_DIR / f"{name.replace('/', '__')}.json"
        if p.exists():
            out[name] = json.loads(p.read_text())
    return out


def _shape(a: str) -> str:
    a = (a or "").strip()
    if a in ("", "...", "<empty>"):
        return "placeholder"
    if a.startswith("lambda"):
        return "lambda"
    if TITLE_CLASS.match(a):
        return "class"
    if DOTTED_CLASSMETHOD.match(a):
        return "classmethod"
    if DOTTED.match(a):
        return "module_alias"
    if IDENT.match(a):
        return "bare"
    return "other"


def _load_csv(name: str) -> dict[str, dict]:
    rows = {}
    with (OUT_DIR / name).open() as fh:
        for r in csv.DictReader(fh):
            rows[r["repo"]] = r
    return rows


def main() -> None:
    reports = _load()
    graphs = _load_csv("rq4_graphs.csv")
    cov = _load_csv("covariates.csv")
    struct = _load_csv("e6_structural.csv")

    rows = []
    for name, rep in reports.items():
        # style per-repo (production scope, matching usage_patterns semantics)
        shapes = {}
        n_dep = 0
        uses_class_dep = False
        uses_current = False
        uses_module_alias = False
        uses_provide = False
        uses_annotated = False
        is_zero_di = True
        has_security = False
        for fr in rep.get("file_details") or []:
            if fr.get("is_test"):
                continue
            if fr.get("annotated_depends"):
                uses_annotated = True
            if fr.get("security_calls"):
                has_security = True
            for c in fr.get("depends_calls") or []:
                s = _shape(c.get("argument", ""))
                shapes[s] = shapes.get(s, 0) + 1
                n_dep += 1
                a = (c.get("argument") or "").strip()
                if TITLE_CLASS.match(a):
                    uses_class_dep = True
                if a.startswith("current_"):
                    uses_current = True
                if a.startswith("provide_"):
                    uses_provide = True
                if DOTTED.match(a) and not DOTTED_CLASSMETHOD.match(a):
                    uses_module_alias = True
        total_calls = rep.get("aggregate", {}).get("depends_total", 0)
        n_sec = rep.get("aggregate", {}).get("security_total", 0)
        n_ann = rep.get("aggregate", {}).get("annotated_depends_total", 0)
        if total_calls or n_sec or n_ann:
            is_zero_di = False
        total = max(sum(shapes.values()), 1)
        p_bare = round(100 * shapes.get("bare", 0) / total, 1)
        p_class = round(100 * shapes.get("class", 0) / total, 1)
        p_module = round(100 * shapes.get("module_alias", 0) / total, 1)
        p_other = round(100 * (total - shapes.get("bare", 0) - shapes.get("class", 0)
                               - shapes.get("module_alias", 0)) / total, 1)

        # graph topology
        g = graphs.get(name, {})
        gb = bool(g) and int(g.get("edges_raw") or 0) > 0
        nodes_clean = int(g.get("nodes_clean") or 0) if gb else 0
        max_depth = int(g.get("max_depth") or 0) if gb else 0
        unresolved = float(g.get("unresolved_pct") or 0) if gb else 0.0
        junk = int(g.get("junk_nodes") or 0) if gb else 0
        density = float(g.get("density") or 0) if gb else 0.0

        # graph-bearing with fan-out >=3 consumers (mirrors _fan_out3 in build_pptx)
        fanout3 = False
        class_nodes = 0
        func_nodes = 0
        if gb:
            fanin = {}
            for e in rep.get("dependency_graph", {}).get("edges", []):
                tgt = e.get("target", "")
                if ":" in tgt:
                    continue
                fanin[tgt] = fanin.get(tgt, 0) + 1
            fanout3 = any(v >= 3 for v in fanin.values())
            for nd in rep.get("dependency_graph", {}).get("nodes", []):
                if nd.get("kind") == "class":
                    class_nodes += 1
                else:
                    func_nodes += 1

        # confounders
        c = cov.get(name, {})
        s = struct.get(name, {})
        stars = safe_int(c.get("stars_gh"))
        created = (c.get("created_at") or "")
        age_months = _age_months(created)
        py_ratio = safe_float(c.get("py_ratio"))
        py_loc = safe_int(s.get("py_loc"))
        py_files = safe_int(s.get("py_files"))
        tutorial = (c.get("tutorial_flag") or "").lower() == "true"

        hygiene = sum([
            (s.get("has_tests") or "").lower() == "true",
            (s.get("has_ci") or "").lower() == "true",
            (s.get("has_precommit") or "").lower() == "true",
            (s.get("has_dockerfile") or "").lower() == "true",
            (s.get("has_compose") or "").lower() == "true",
        ])
        soph = safe_int(s.get("sophistication_index"))
        integration = safe_int(s.get("integration_count"))

        rows.append({
            "repo": name,
            "n_dep": n_dep,
            "n_security": n_sec,
            "n_annotated": n_ann,
            "p_bare": p_bare, "p_class": p_class, "p_module": p_module, "p_other": p_other,
            "is_zero_di": int(is_zero_di),
            "uses_class_dep": int(uses_class_dep),
            "uses_current": int(uses_current),
            "uses_module_alias": int(uses_module_alias),
            "uses_provide": int(uses_provide),
            "has_security": int(has_security),
            "uses_annotated": int(uses_annotated),
            "graph_bearing": int(gb),
            "nodes_clean": nodes_clean,
            "func_nodes": func_nodes,
            "class_nodes": class_nodes,
            "class_node_ratio": round(100 * class_nodes / max(class_nodes + func_nodes, 1), 2),
            "max_depth": max_depth,
            "unresolved_pct": unresolved,
            "junk_nodes": junk,
            "density": round(density, 4),
            "fanout3": int(fanout3),
            "stars_gh": stars,
            "age_months": age_months,
            "py_ratio": py_ratio,
            "py_loc": py_loc,
            "py_files": py_files,
            "tutorial_flag": int(tutorial),
            "has_tests": int((s.get("has_tests") or "").lower() == "true"),
            "hygiene": hygiene,
            "sophistication_index": soph,
            "integration_count": integration,
        })

    rows.sort(key=lambda r: r["repo"])
    with (OUT_DIR / "pattern_features.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    zd = sum(r["is_zero_di"] for r in rows)
    gb = sum(r["graph_bearing"] for r in rows)
    fo = sum(r["fanout3"] for r in rows)
    print(f"[pattern_features] {n} repos; zero-DI {zd} ({round(100*zd/n,1)}%); "
          f"graph-bearing {gb} ({round(100*gb/n,1)}%); fanout>=3 {fo} "
          f"({round(100*fo/max(gb,1),1)}% of graph-bearing)")
    print("   wrote analysis/out/pattern_features.csv")


def safe_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _age_months(created: str) -> float:
    # created ISO datetime or date; approximate months to epoch
    try:
        import datetime as _dt
        ts = created[:19]
        if "T" in ts:
            dt = _dt.datetime.fromisoformat(ts)
        else:
            dt = _dt.date.fromisoformat(ts[:10])
            dt = _dt.datetime(dt.year, dt.month, dt.day)
        days = (_dt.datetime.now(_dt.timezone.utc) - dt.replace(tzinfo=_dt.timezone.utc)).days
        return round(days / 30.44, 1)
    except Exception:
        return 0.0


if __name__ == "__main__":
    main()
