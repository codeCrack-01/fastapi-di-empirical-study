"""
analysis/render_sample_inputs.py — Phase 2 LLM-input renderer.

For each repo in the frozen stratified sample, render a COMPACT pattern-evidence
summary from its STORED extractor report (corpus/reports/*.json), plus the
deterministic C1-C4 / EX2 / zero-DI baseline. The extractor is NOT re-run and no
raw codebase is shipped to the LLM: the evidence is the report's own fields.

Outputs (analysis/out/):
  llm_input/sample_<owner>__<repo>.json   per-repo evidence + baseline
  llm_input/input_index.json              index + a summary row per repo
  llm_input/known_baseline.csv            per-repo C1-C4 flags/counts (peer review)

Usage:
    uv run python analysis/render_sample_inputs.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "novelty"))
from fingerprints import arg_shape  # noqa: E402
from labels import CATALOG  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
INPUT_DIR = OUT / "llm_input"
REPORTS = ROOT.parent / "corpus" / "reports"

CATALOG_KEYS = {cid: key for cid, _n, key in CATALOG}
EX2_KEY = "non_fastapi_depends_sources"


def render_repo(full_name: str) -> dict:
    report = json.loads((REPORTS / (full_name.replace("/", "__") + ".json")).read_text())
    agg = report.get("aggregate", {})
    graph = report.get("dependency_graph", {})

    known = [cid for cid, key in CATALOG_KEYS.items() if agg.get(key, 0) > 0]
    ex2 = agg.get(EX2_KEY, 0) if EX2_KEY in agg else _sum_ex2(report)
    zero_di = not known

    shapes: dict[str, int] = {}
    yield_deps: dict[str, int] = {}
    scopes: dict[str, int] = {}
    for f in report.get("file_details", []):
        for c in f.get("depends_calls", []):
            shape = arg_shape(c.get("argument"))
            shapes[shape] = shapes.get(shape, 0) + 1
        for s in f.get("security_calls", []):
            scope = ", ".join(sorted(s.get("scopes") or [])) or "<no-scopes>"
            scopes[scope] = scopes.get(scope, 0) + 1
        for y in f.get("yield_functions", []):
            if not y.get("used_as_dependency"):
                continue
            key = y.get("name") or "yield-fn"
            yield_deps[key] = yield_deps.get(key, 0) + 1

    return {
        "full_name": full_name,
        "report_path": str(REPORTS / (full_name.replace("/", "__") + ".json")),
        "schema_version": report.get("schema_version"),
        "extractor_version": report.get("extractor_version"),
        "coverage": report.get("coverage", {}),
        "aggregate": {k: agg.get(k, 0) for k in CATALOG_KEYS.values()},
        "known": known,
        "ex2_flag": ex2 > 0,
        "ex2_sources": _ex2_names(report),
        "zero_di": zero_di,
        "catalog_baseline": "; ".join(known) if known else ("ZERO-DI" if zero_di else "-"),
        "arg_shapes": shapes,
        "security_scopes": scopes,
        "yield_function_names": list(sorted(yield_deps)),
        "n_yield_functions": len(yield_deps),
        "dependency_graph": {
            "nodes": len(graph.get("nodes", [])),
            "edges": len(graph.get("edges", [])),
            "max_depth": graph.get("max_depth"),
            "unresolved_depends": graph.get("unresolved_depends"),
        },
        "observations": report.get("observations", []),
    }


def _sum_ex2(report: dict) -> int:
    n = 0
    for f in report.get("file_details", []):
        n += len(f.get(EX2_KEY, {}))
    return n


def _ex2_names(report: dict) -> list[str]:
    seen: dict[str, int] = {}
    for f in report.get("file_details", []):
        for src, cnt in (f.get(EX2_KEY, {}) or {}).items():
            seen[src] = seen.get(src, 0) + (cnt if isinstance(cnt, int) else len(cnt))
    return [s for s, _ in sorted(seen.items(), key=lambda kv: -kv[1])]


def main():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    sample = json.loads((OUT / "sample.json").read_text())
    strata = {s["id"]: s["weight"] for s in sample["strata"]}
    rows = []
    by_repo = {}
    for r in sample["sampled"]:
        full = r["full_name"]
        data = render_repo(full)
        data["stratum"] = r["stratum"]
        data["weight"] = r["weight"]
        fname = "sample_" + full.replace("/", "__") + ".json"
        (INPUT_DIR / fname).write_text(json.dumps(data, indent=2))
        by_repo[full] = {"file": fname, "stratum": r["stratum"],
                         "known_baseline": data["catalog_baseline"],
                         "depends_total": data["aggregate"].get("depends_total", 0),
                         "nodes": data["dependency_graph"]["nodes"],
                         "edges": data["dependency_graph"]["edges"]}
        rows.append({**by_repo[full], "weight": r["weight"]})

    (INPUT_DIR / "known_baseline.csv").write_text(
        _csv(rows)
    )
    index = {
        "schema_version": "0.2",
        "sample_pool": sample["pool_size"],
        "sample_size": len(by_repo),
        "strata_weights": strata,
        "repos": by_repo,
    }
    (INPUT_DIR / "input_index.json").write_text(json.dumps(index, indent=2))
    print(f"[render] {len(by_repo)} repos -> {INPUT_DIR}")


def _csv(rows) -> str:
    out = []
    cols = ["file", "stratum", "known_baseline", "depends_total", "nodes", "edges", "weight"]
    w = csv.writer(io := __import__("io").StringIO())
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(c, "") for c in cols])
    return io.getvalue()


if __name__ == "__main__":
    main()