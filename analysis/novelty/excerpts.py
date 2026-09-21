"""analysis/novelty/excerpts.py — deterministic per-repo source-excerpt packer.

For the 327-repo stratified sample, packs the ACTUAL source code around every
DI-adjacent extractor node (C1..C4 constructs) — pinned to each repo's
``commit_sha`` — into one compact, shippable artifact:

    analysis/novelty/out/novelty_repo_context.json

The remote executor consumes ONLY this file to run the two-pass per-repo
check; it never needs the corpus, the clones, an internet connection, or a
"memory flow". Everything is deterministic (fixed iteration order, pinned
commits, no randomness), so the artifact reproduces byte-for-byte.

usage:
    python analysis/novelty/excerpts.py [--out analysis/novelty/out]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
OUT_DIR = _HERE / "out"
ANALYSIS_OUT = _HERE.parent / "out"                      # analysis/out
SAMPLE_JSON = ANALYSIS_OUT / "sample.json"
CORPUS_REPORTS = _HERE.parent.parent / "corpus" / "reports"  # corpus/reports

DI_FILE_KEYS = [
    ("C1", "depends_calls"),
    ("C2", "security_calls"),
    ("C3", "annotated_depends"),
    ("C4", "yield_functions"),
]

EXCERPT_HALF = 14          # +- lines around the node
EXCERPT_CAP = 48           # max excerpts packed per repo (deterministic head)
MAX_FILE_BYTES = 1_500_000

schema_version = "0.1"


def _load_sample() -> dict[str, dict]:
    """full_name -> {stratum, weight} for the 327 sample repos (seed 42)."""
    data = json.loads(SAMPLE_JSON.read_text())
    out: dict[str, dict] = {}
    for r in data["sampled"]:
        out[r["full_name"]] = {"stratum": r.get("stratum"), "weight": r.get("weight")}
    return out


def _slurp_excerpt(path: str | None, line: int, half: int = EXCERPT_HALF) -> tuple[str, int, int] | None:
    """Return (text, start_line, end_line) around a 1-based line, or None."""
    if not path:
        return None
    try:
        st = Path(path).stat()
        if st.st_size > MAX_FILE_BYTES:
            return None
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    if not lines:
        return None
    start = max(1, line - half)
    end = min(len(lines), line + half)
    if start > end:
        return None
    text = "\n".join(lines[start - 1:end]).rstrip()
    return text, start, end


def _rel_path(path: str | None, repo_id: str | None) -> str | None:
    from fingerprints import _rel_file_path
    return _rel_file_path(path, repo_id)


def build_repo_context(sample: dict[str, dict], reports_dir: Path | None = None) -> list[dict]:
    from fingerprints import github_url_for, _node_occurrence, fingerprint_for
    from fingerprints import _rel_file_path

    reports_dir = reports_dir or CORPUS_REPORTS
    repos: list[dict] = []

    for full_name in sorted(sample):
        name = full_name.replace("/", "__")
        report_path = reports_dir / f"{name}.json"
        if not report_path.exists():
            continue
        try:
            report = json.loads(report_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue

        repo = report.get("repo") if isinstance(report.get("repo"), dict) else {}
        sha = repo.get("commit_sha")
        aggregate = report.get("aggregate", {})
        coverage = report.get("coverage", {})
        dg = report.get("dependency_graph", {}) or {}

        nodes: list[dict] = []
        for cid, key in DI_FILE_KEYS:
            for fr in report.get("file_details", []):
                fpath = fr.get("path") or ""
                for node in fr.get(key, []):
                    fp = fingerprint_for(node, cid)
                    occ = _node_occurrence(full_name, node, cid,
                                           file=_rel_path(fpath, name) or None,
                                           github_url=github_url_for(repo, full_name,
                                                                     _rel_path(fpath, name),
                                                                     node.get("line")) or None)
                    nodes.append({
                        "construct": cid,
                        "fingerprint": fp,
                        "file": _rel_path(fpath, name),
                        "path": fpath,
                        "line": node.get("line"),
                        "context_function": node.get("context_function") or node.get("name"),
                        "github_url": occ.get("github_url"),
                    })

        # deterministic matched-fingerprint rollup (head of the node stream)
        matched: dict[str, dict] = {}
        for n in nodes:
            m = matched.setdefault(n["fingerprint"], {
                "fingerprint": n["fingerprint"], "construct": n["construct"],
                "n": 0, "urls": [],
            })
            m["n"] += 1
            if len(m["urls"]) < 3 and n.get("github_url"):
                m["urls"].append(n["github_url"])

        excerpts: list[dict] = []
        for n in nodes:
            if len(excerpts) >= EXCERPT_CAP:
                break
            loc = _slurp_excerpt(n["path"], n["line"])
            excerpts.append({
                "construct": n["construct"],
                "fingerprint": n["fingerprint"],
                "file": n["file"],
                "line": n["line"],
                "context_function": n["context_function"],
                "github_url": n["github_url"],
                "excerpt": loc[0] if loc else None,
                "start_line": loc[1] if loc else None,
                "end_line": loc[2] if loc else None,
            })

        sample_info = sample[full_name]
        repos.append({
            "full_name": full_name,
            "stratum": sample_info.get("stratum"),
            "weight": sample_info.get("weight"),
            "commit_sha": sha,
            "summary": {
                "depends_total": aggregate.get("depends_total", 0),
                "security_total": aggregate.get("security_total", 0),
                "annotated_depends_total": aggregate.get("annotated_depends_total", 0),
                "yield_dep_total": aggregate.get("yield_dep_total", 0),
                "files_total": coverage.get("files_total"),
                "files_production": coverage.get("files_production"),
                "pct_production": coverage.get("pct_production"),
                "unresolved_depends": (len(dg["unresolved_depends"])
                                       if isinstance(dg.get("unresolved_depends"), list)
                                       else dg.get("unresolved_depends")),
                "max_depth": dg.get("max_depth"),
            },
            "source_excerpts": excerpts,
            "matched_fingerprints": sorted(matched.values(), key=lambda m: (-m["n"], m["fingerprint"])),
            "n_di_nodes": len(nodes),
        })

    return repos


def write_artifact(repos: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_exc = sum(len(r["source_excerpts"]) for r in repos)
    payload = {
        "schema_version": schema_version,
        "source_sample": str(SAMPLE_JSON),
        "n_repos": len(repos),
        "n_excerpts": n_exc,
        "excerpt_half": EXCERPT_HALF,
        "excerpt_cap": EXCERPT_CAP,
        "repos": repos,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Pack per-repo source excerpts (327-sample)")
    ap.add_argument("--out", default=str(OUT_DIR / "novelty_repo_context.json"))
    args = ap.parse_args()

    sample = _load_sample()
    repos = build_repo_context(sample)
    write_artifact(repos, Path(args.out))
    n_exc = sum(len(r["source_excerpts"]) for r in repos)
    n_miss = sum(1 for r in repos for e in r["source_excerpts"] if not e["excerpt"])
    print(f"[excerpts] {len(repos)} repos, {n_exc} excerpts ({n_miss} missing clones), "
          f"-> {Path(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())