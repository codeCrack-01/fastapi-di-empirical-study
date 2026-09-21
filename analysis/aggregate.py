"""
analysis/aggregate.py — Corpus-level aggregation for the study sample.

Consumes the artifacts already produced by the pipeline (no network, no
re-cloning):
  corpus/manifest.json   accepted repos + metadata + extractor aggregates
  corpus/reports/*.json  full extractor report per accepted repo
  analysis/out/sample.json  drawn by analysis/sample.py

Produces paper-facing tables in analysis/out/:
  rq1_constructs.csv  construct prevalence (C1-C9 + extras, zero-DI cohort)
  rq4_graphs.csv      dependency-graph complexity per repo  (legacy filename; feeds RQ3)
  covariates.csv      per-repo metadata joined for post-hoc analyses
  sensitivity.csv     headline statistics re-run at every E5 threshold
  summary.md          human-readable digest of the above

RQ2 (usage & dynamic relationships) is produced separately by
analysis/usage_patterns.py → analysis/out/usage_patterns.csv + _summary.md.

All orderings are sorted for byte-stable, reproducible outputs.

Usage:
    uv run python analysis/sample.py            # draw sample first
    uv run python analysis/aggregate.py         # then aggregate
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics as st
import sys
from pathlib import Path

# Sensitivity thresholds for the E5 (scale) eligibility rule removed from
# settings.py during the schema-0.2 migration. Kept here with the historical
# values so the census sensitivity table stays comparable to the 402-era paper.
E5_MIN_FASTAPI_APPS = 1
E5_SENSITIVITY_THRESHOLDS = [2, 3, 4, 5, 6, 8]

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

CONSTRUCTS = [
    ("C1", "Depends", "depends_total"),
    ("C2", "Security", "security_total"),
    ("C3", "Annotated dependency", "annotated_depends_total"),
    ("C4", "Generator/yield dependency", "yield_dep_total"),
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

    nfapi_repos = nfapi_sources = 0
    di_any = []
    for r in reports.values():
        nfs = [s for f in r.get("file_details", []) for s in f.get("non_fastapi_depends_sources", {})]
        nfapi_repos += bool(nfs)
        nfapi_sources += len(nfs)
        a = r["aggregate"]
        di_any.append(a.get("depends_total", 0) + a.get("security_total", 0) + a.get("annotated_depends_total", 0))

    extra = [
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


JUNK_NODE_RE = re.compile(r"[:/\\]")


def split_edges(nodes: list[dict], edges: list[dict]) -> tuple[list[dict], list[dict]]:
    """Drop resolver-emitted junk nodes and any edge referencing them.

    Junk nodes are anonymous ``{file_path}:{line}`` placeholders produced by
    the resolver when a Depends call has no ``context_function`` (module-scope
    declarations such as ``FastAPI(dependencies=[...])`` or router defaults).
    They are identified by containing a path separator or a ``file:line``
    anchor that no clean callable name carries.
    """
    clean_ids = {n["id"] for n in nodes if not JUNK_NODE_RE.search(n["id"])}
    clean_nodes = [n for n in nodes if n["id"] in clean_ids]
    clean_edges = [
        e for e in edges
        if e["source"] in clean_ids and e["target"] in clean_ids
    ]
    return clean_nodes, clean_edges


def _stars_bucket(stars) -> str:
    stars = stars or 0
    if stars == 0:
        return "0"
    if stars < 10:
        return "1-9"
    if stars < 100:
        return "10-99"
    return "100+"


def _age_bucket(created_at) -> str:
    from datetime import datetime
    if not created_at:
        return "unknown"
    ref = datetime(2026, 8, 17)
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
        months = (ref.year - created.year) * 12 + (ref.month - created.month)
    except (ValueError, TypeError):
        return "unknown"
    if months < 12:
        return "<12mo"
    if months < 36:
        return "12-36mo"
    return "36mo+"


CORE_KEYS = ("depends_total", "security_total", "annotated_depends_total")


def disaggregate_rows(sample: list[str], reports: dict, manifest: dict, axis: str) -> list[dict]:
    """RQ1 covariate axis (folded application-class question): core-DI prevalence per covariate bucket.

    ``axis`` is "age" (created_at months) or "stars".
    """
    from datetime import datetime
    by_name = {a["full_name"]: a for a in manifest["accepted"]}
    bucket_fn = _stars_bucket if axis == "stars" else _age_bucket
    bucket_field = "stars_gh" if axis == "stars" else "created_at"

    buckets: dict[str, list[str]] = {}
    for name in sorted(sample):
        meta = by_name.get(name, {})
        buckets.setdefault(bucket_fn(meta.get(bucket_field)), []).append(name)

    def _total(r, keys):
        return sum(r["aggregate"].get(k, 0) for k in keys)

    rows = []
    for bucket in sorted(buckets, key=lambda b: (b not in ("0", "<12mo"), b)):
        names = buckets[bucket]
        reps = {n: reports[n] for n in names if n in reports}
        n = len(names)
        core_users = sum(1 for r in reps.values() if _total(r, CORE_KEYS) > 0)
        depends_users = sum(1 for r in reps.values() if r["aggregate"].get("depends_total", 0) > 0)
        med = st.median([_total(r, CORE_KEYS) for r in reps.values()]) if reps else 0
        rows.append(
            {
                f"{axis}_bucket": bucket,
                "repos": n,
                "repos_using_core_di": core_users,
                "pct_using_core_di": round(100 * core_users / max(n, 1), 1),
                "repos_using_depends": depends_users,
                "pct_using_depends": round(100 * depends_users / max(n, 1), 1),
                "median_core_calls": round(med, 1),
            }
        )
    return rows


def rq4_rows(reports: dict) -> list[dict]:
    rows = []
    for name in sorted(reports):
        g = reports[name]["dependency_graph"]
        raw_nodes = g["nodes"]
        raw_edges = g["edges"]
        clean_nodes, clean_edges = split_edges(raw_nodes, raw_edges)
        raw_n, clean_n = len(raw_nodes), len(clean_nodes)
        raw_e, clean_e = len(raw_edges), len(clean_edges)

        # Unresolved is reported against edges that point at resolvable targets;
        # keep the raw figure but flag repos with no clean nodes.
        unresolved = g["unresolved_depends"]
        denom = clean_e + unresolved
        rows.append(
            {
                "repo": name,
                "nodes_raw": raw_n,
                "nodes_clean": clean_n,
                "junk_nodes": raw_n - clean_n,
                "edges_raw": raw_e,
                "edges_clean": clean_e,
                "max_depth": g["max_depth"],
                "unresolved_depends": unresolved,
                "unresolved_pct": round(100 * unresolved / max(denom, 1), 1),
                "density": round(clean_e / (clean_n * (clean_n - 1)), 4) if clean_n > 1 else 0.0,
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
    nonempty = [r for r in rq4 if r["nodes_clean"] > 0]
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
        "## RQ3 — dependency-graph complexity (clean nodes, non-empty graphs)",
        "",
        f"- Graph-bearing repos (clean): {len(nonempty)} / {len(rq4)}",
    ]
    if nonempty:
        nodes = [r["nodes_clean"] for r in nonempty]
        depth = [r["max_depth"] for r in nonempty]
        unres = [r["unresolved_pct"] for r in nonempty]
        junk_total = sum(r["junk_nodes"] for r in rq4)
        junk_repos = sum(1 for r in rq4 if r["junk_nodes"] > 0)
        lines += [
            f"- Nodes (clean): median {st.median(nodes)}, IQR {iqr(nodes)}, max {max(nodes)}",
            f"- Max depth: median {st.median(depth)}, max {max(depth)}",
            f"- Unresolved %: median {st.median(unres):.1f}",
            "",
            f"- Junk nodes filtered: {junk_total} across {junk_repos}/{len(rq4)} repos "
            "(module-scope file:line placeholders from the resolver)",
        ]
    out.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Aggregate reports into paper tables")
    ap.add_argument("--sample", default=str(OUT_DIR / "sample.json"))
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--reports", default=str(ROOT.parent / "corpus" / "reports"))
    ap.add_argument(
        "--scope", choices=("sample", "all"), default="sample",
        help="'sample' restricts to the seed-42 drawn sample; 'all' aggregates the "
             "entire accepted corpus (census). Denominator for pct columns is always "
             "the number of repos actually aggregated.",
    )
    args = ap.parse_args()

    sample_payload = json.loads(Path(args.sample).read_text())
    manifest = json.loads(Path(args.manifest).read_text())

    if args.scope == "all":
        names = sorted(a["full_name"] for a in manifest["accepted"])
        sample_payload = dict(sample_payload)
        sample_payload["sample_size"] = len(names)
        sample_payload["pool_size"] = len(names)
        sample_payload["method"] = "full-corpus census (not a sample)"
        sample_payload["seed"] = None
    else:
        entries = sample_payload["sampled"]
        names = sorted(
            e["full_name"] if isinstance(e, dict) else e for e in entries
        )

    reports, missing = load_reports(names, Path(args.reports))
    if missing:
        print(f"[aggregate] WARNING: {len(missing)} repos have no report: {missing}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rq1 = rq1_rows(reports)
    rq4 = rq4_rows(reports)

    write_csv(OUT_DIR / "rq1_constructs.csv", rq1)
    write_csv(OUT_DIR / "rq4_graphs.csv", rq4)
    write_csv(OUT_DIR / "covariates.csv", covariate_rows(names, manifest))
    sens = sensitivity_rows(manifest)
    write_csv(OUT_DIR / "sensitivity.csv", sens)
    write_csv(OUT_DIR / "rq1_by_stars.csv", disaggregate_rows(names, reports, manifest, "stars"))
    write_csv(OUT_DIR / "rq1_by_age.csv", disaggregate_rows(names, reports, manifest, "age"))
    write_summary(OUT_DIR / "summary.md", sample_payload, reports, missing, rq1, rq4)

    print(f"[aggregate] scope={args.scope} {len(reports)} reports aggregated -> {OUT_DIR}/")
    for f in ("rq1_constructs.csv", "rq4_graphs.csv", "covariates.csv", "sensitivity.csv",
              "rq1_by_stars.csv", "rq1_by_age.csv", "summary.md"):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
