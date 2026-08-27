"""
analysis/aggregate.py — Corpus-level aggregation for the study sample.

Consumes the artifacts already produced by the pipeline (no network, no
re-cloning):
  corpus/manifest.json   accepted repos + metadata + extractor aggregates
  corpus/reports/*.json  full extractor report per accepted repo
  analysis/out/sample.json  drawn by analysis/sample.py

Produces paper-facing tables in analysis/out/:
  rq1_constructs.csv  construct prevalence (C1-C9 + extras, zero-DI cohort)
  rq4_graphs.csv      dependency-graph complexity per repo
  covariates.csv      per-repo metadata joined for post-hoc analyses
  sensitivity.csv     headline statistics re-run at every E5 threshold
  summary.md          human-readable digest of the above

All orderings are sorted for byte-stable, reproducible outputs.

Usage:
    uv run python analysis/sample.py            # draw sample first
    uv run python analysis/aggregate.py         # then aggregate
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "corpus"))
from settings import E5_MIN_FASTAPI_APPS, E5_SENSITIVITY_THRESHOLDS  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

CONSTRUCTS = [
    ("C1", "Depends", "depends_total"),
    ("C2", "Security", "security_total"),
    ("C3", "Annotated dependency", "annotated_depends_total"),
    ("C4", "Generator/yield dependency", "yield_dep_total"),
    ("C5", "Router-level dependency", "router_dep_total"),
    ("C6", "App-level dependency", "app_dep_total"),
    ("C7", "Dependency override", "override_total"),
    ("C8", "Callable class dependency", "callable_class_dep_total"),
]


def iqr(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        return (values[0] if values else 0.0, values[0] if values else 0.0)
    q1, _, q3 = st.quantiles(values, n=4)
    return q1, q3


def load_reports(names: list[str], reports_dir: Path):
    reports, missing = {}, []
    for name in names:
        p = reports_dir / f"{name.replace('/', '__')}.json"
        if p.exists():
            reports[name] = json.loads(p.read_text())
        else:
            missing.append(name)
    return reports, sorted(missing)


def rq1_rows(reports: dict) -> list[dict]:
    rows = []
    for cid, label, key in CONSTRUCTS:
        counts = [r["aggregate"].get(key, 0) for r in reports.values()]
        users = [c for c in counts if c > 0]
        q1, q3 = iqr([float(c) for c in users])
        rows.append(
            {
                "construct_id": cid,
                "construct": label,
                "repos_using": len(users),
                "pct_of_sample": round(100 * len(users) / max(len(reports), 1), 1),
                "total_calls": sum(counts),
                "median_per_repo_using": st.median(users) if users else 0,
                "q1_per_repo_using": round(q1, 1),
                "q3_per_repo_using": round(q3, 1),
                "max": max(counts) if counts else 0,
                "source": "aggregate",
            }
        )

    wrap_repos = wrap_total = 0
    nfapi_repos = nfapi_sources = 0
    di_any = []
    for r in reports.values():
        wraps = [w for f in r.get("file_details", []) for w in f.get("dynamic_framework_wrappers", [])]
        nfs = [s for f in r.get("file_details", []) for s in f.get("non_fastapi_depends_sources", {})]
        wrap_repos += bool(wraps)
        wrap_total += len(wraps)
        nfapi_repos += bool(nfs)
        nfapi_sources += len(nfs)
        a = r["aggregate"]
        di_any.append(a.get("depends_total", 0) + a.get("security_total", 0) + a.get("annotated_depends_total", 0))

    extra = [
        ("EX1", "Dynamic framework wrappers", wrap_repos, wrap_total),
        ("EX2", "Non-FastAPI Depends sources", nfapi_repos, nfapi_sources),
        (
            "Z",
            "Repos using ZERO core DI constructs (no Depends/Security/Annotated)",
            sum(1 for d in di_any if d == 0),
            None,
        ),
    ]
    for cid, label, repos, total in extra:
        rows.append(
            {
                "construct_id": cid,
                "construct": label,
                "repos_using": repos,
                "pct_of_sample": round(100 * repos / max(len(reports), 1), 1),
                "total_calls": total if total is not None else "",
                "median_per_repo_using": "",
                "q1_per_repo_using": "",
                "q3_per_repo_using": "",
                "max": "",
                "source": "file_details" if cid != "Z" else "derived",
            }
        )
    return rows


def rq4_rows(reports: dict) -> list[dict]:
    rows = []
    for name in sorted(reports):
        g = reports[name]["dependency_graph"]
        nodes, edges = len(g["nodes"]), len(g["edges"])
        dens = edges / (nodes * (nodes - 1)) if nodes > 1 else 0.0
        rows.append(
            {
                "repo": name,
                "nodes": nodes,
                "edges": edges,
                "max_depth": g["max_depth"],
                "unresolved_depends": g["unresolved_depends"],
                "unresolved_pct": round(100 * g["unresolved_depends"] / max(edges + g["unresolved_depends"], 1), 1),
                "density": round(dens, 4),
            }
        )
    return rows


def covariate_rows(sample: list[str], manifest: dict) -> list[dict]:
    by_name = {a["full_name"]: a for a in manifest["accepted"]}
    rows = []
    for name in sorted(sample):
        a = by_name[name]
        rows.append(
            {
                "repo": name,
                "stars_gh": a.get("stars_gh"),
                "stars_libio": a.get("stars_libio"),
                "forks_gh": a.get("forks_gh"),
                "created_at": a.get("created_at"),
                "pushed_at": a.get("pushed_at"),
                "commit_count": a.get("commit_count"),
                "py_ratio": a.get("py_ratio"),
                "license": a.get("license"),
                "tutorial_flag": a.get("tutorial_flag", False),
                "files_importing_fastapi": a["aggregate"]["files_importing_fastapi"],
                "fastapi_app_count": a["aggregate"]["fastapi_app_count"],
                "pct_production_coverage": a["coverage"]["pct_production"],
            }
        )
    return rows


def sensitivity_rows(manifest: dict) -> list[dict]:
    accepted = manifest["accepted"]
    rows = []
    for t in E5_SENSITIVITY_THRESHOLDS:
        elig = [
            a for a in accepted
            if a["aggregate"]["files_importing_fastapi"] >= t
            and a["aggregate"]["fastapi_app_count"] >= E5_MIN_FASTAPI_APPS
        ]
        dep = [
            a["aggregate"]["depends_total"] + a["aggregate"]["security_total"]
            + a["aggregate"]["annotated_depends_total"]
            for a in elig
        ]
        users = [d for d in dep if d > 0]
        rows.append(
            {
                "e5_min_fastapi_files": t,
                "eligible_n": len(elig),
                "pct_using_core_di": round(100 * len(users) / max(len(elig), 1), 1),
                "median_depends_total_incl_zero": st.median(dep) if dep else 0,
                "median_depends_among_users": st.median(users) if users else 0,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_summary(out: Path, sample_meta: dict, reports: dict, missing: list[str], rq1: list[dict], rq4: list[dict]):
    nonempty = [r for r in rq4 if r["nodes"] > 0]
    lines = [
        "# Extraction summary",
        "",
        f"- Sample: {sample_meta['sample_size']} of pool {sample_meta['pool_size']}"
        f" ({sample_meta['method']}"
        + (f", seed={sample_meta['seed']})" if sample_meta['seed'] is not None else ")")
        + "",
        f"- Reports loaded: {len(reports)}" + (f"; MISSING: {', '.join(missing)}" if missing else ""),
        "",
        "## RQ1 — construct prevalence (top rows)",
        "",
        "| Construct | Repos | % | Total calls | Median (users) |",
        "|---|---|---|---|---|",
    ]
    for r in rq1[:9]:
        lines.append(f"| {r['construct']} | {r['repos_using']} | {r['pct_of_sample']}% | {r['total_calls']} | {r['median_per_repo_using']} |")
    z = next((r for r in rq1 if r["construct_id"] == "Z"), None)
    if z:
        lines += ["", f"**Zero-DI cohort:** {z['repos_using']} repos ({z['pct_of_sample']}%) use no Depends/Security/Annotated at all."]
    lines += [
        "",
        "## RQ4 — dependency-graph complexity (repos with non-empty graphs)",
        "",
        f"- Graph-bearing repos: {len(nonempty)} / {len(rq4)}",
    ]
    if nonempty:
        nodes = [r["nodes"] for r in nonempty]
        depth = [r["max_depth"] for r in nonempty]
        unres = [r["unresolved_pct"] for r in nonempty]
        lines += [
            f"- Nodes: median {st.median(nodes)}, IQR {iqr(nodes)}, max {max(nodes)}",
            f"- Max depth: median {st.median(depth)}, max {max(depth)}",
            f"- Unresolved %: median {st.median(unres):.1f}",
        ]
    out.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Aggregate sample reports into paper tables")
    ap.add_argument("--sample", default=str(OUT_DIR / "sample.json"))
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--reports", default=str(ROOT.parent / "corpus" / "reports"))
    args = ap.parse_args()

    sample_payload = json.loads(Path(args.sample).read_text())
    sampled = sorted(sample_payload["sampled"])
    manifest = json.loads(Path(args.manifest).read_text())
    reports, missing = load_reports(sampled, Path(args.reports))
    if missing:
        print(f"[aggregate] WARNING: {len(missing)} sampled repos have no report: {missing}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rq1 = rq1_rows(reports)
    rq4 = rq4_rows(reports)

    write_csv(OUT_DIR / "rq1_constructs.csv", rq1)
    write_csv(OUT_DIR / "rq4_graphs.csv", rq4)
    write_csv(OUT_DIR / "covariates.csv", covariate_rows(sampled, manifest))
    sens = sensitivity_rows(manifest)
    write_csv(OUT_DIR / "sensitivity.csv", sens)
    write_summary(OUT_DIR / "summary.md", sample_payload, reports, missing, rq1, rq4)

    print(f"[aggregate] {len(reports)} reports aggregated -> {OUT_DIR}/")
    for f in ("rq1_constructs.csv", "rq4_graphs.csv", "covariates.csv", "sensitivity.csv", "summary.md"):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
