"""analysis/novelty/fingerprints.py — canonical fingerprints from extractor reports.

A *fingerprint* is the canonical shape of one DI construct occurrence: the
catalog rule (C1-C4/EX2/Z) that produced the node plus the structural slots
that distinguish one *usage pattern* from another. Identifier names are mapped
to SHAPE classes (BARE / DOTTED / CLASS / CALL / EMPTY / ELLIPSIS), so the
fingerprint is repo-independent: e.g. ``Depends(get_db)`` and
``Depends(session_factory)`` collapse to the same fingerprint because they are
the same pattern, while ``Depends(current(P))``-shaped nests stay separate.

Router- and app-level ``dependencies=[...]`` wiring, dependency overrides and
callable-class dependencies are **compositions of C1/C2**, not catalogue
constructs, so they no longer produce fingerprints of their own.

The extractor stores resolved argument strings (``core.current_principal``,
``get_db``, ``<empty>``, ``...``) and qualifier fields (``in_signature``,
``scopes``, router/app dependency lists, annotated type). We never mutate the
extractor mid-crawl (reconstitution is live); canonicalization is computed
here from the stored fields only.

Output groups: because identical patterns collapse, ``OCCURRENCES`` (count)
and per-fingerprint representative code examples are kept so an annotator can
see real code while every *distinct* signature is classified exactly once.

Consumed by:
    select_panel.py   -> candidate-rater qualification on anchor fingerprints
    annotate.py       -> exhaustive full-corpus fingerprint annotation
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

REPORTS_DIR = Path(__file__).resolve().parents[2] / "corpus" / "reports"
MANIFEST = Path(__file__).resolve().parents[2] / "corpus" / "manifest.json"
EXAMPLES_PER_FP = 5

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TITLE = re.compile(r"^[A-Z][A-Za-z0-9_]*$")


def arg_shape(argument: str) -> str:
    """Map a stored argument string to a structural shape class."""
    a = (argument or "").strip()
    if a in ("<empty>", ""):
        return "EMPTY"
    if a == "..." or a.startswith("<"):
        return "ELLIPSIS" if a == "..." else "OTHER"
    if "(" in a:
        return "CALL"
    if "." in a:
        return "DOTTED"
    if IDENT.match(a):
        return "CLASS" if TITLE.match(a) else "BARE"
    return "OTHER"


def _scopes_key(scopes: list[str] | None) -> str:
    scopes = sorted(s for s in (scopes or []) if s)
    return ",".join(scopes) if scopes else ""


def fingerprint_c1(node: dict) -> str:
    sig = "SIG" if node.get("in_signature") else "PARAM"
    return f"C1|{arg_shape(node.get('argument'))}|{sig}"


def fingerprint_c2(node: dict) -> str:
    return f"C2|{arg_shape(node.get('argument'))}|{_scopes_key(node.get('scopes')) or 'ascopes'}"


def fingerprint_c3(node: dict) -> str:
    ann = arg_shape(node.get("annotated_type"))
    dep = arg_shape(node.get("depends_argument"))
    return f"C3|{ann}|{dep}"


def fingerprint_c4(node: dict) -> str:
    return "C4|USED" if node.get("used_as_dependency") else "C4|DEF"


def fingerprint_for(node: dict, construct: str) -> str:
    fn = {
        "C1": fingerprint_c1,
        "C2": fingerprint_c2,
        "C3": fingerprint_c3,
        "C4": fingerprint_c4,
    }[construct]
    return fn(node)


def _node_occurrence(name: str, node: dict, construct: str,
                     file: str | None = None, github_url: str | None = None) -> dict:
    fp = fingerprint_for(node, construct)
    occ = {
        "construct": construct,
        "fingerprint": fp,
        "repo": name,
        "line": node.get("line"),
        "context_function": node.get("context_function"),
        "argument": node.get("argument") or node.get("class_name") or node.get("name"),
        "annotated_type": node.get("annotated_type"),
        "dependencies": node.get("dependencies"),
        "scopes": node.get("scopes"),
    }
    if file:
        occ["file"] = file
    if github_url:
        occ["github_url"] = github_url
    return occ


def _rel_file_path(path: str | None, repo_id: str | None) -> str | None:
    """Strip the local clone prefix off a stored path, giving ``owner/repo/file.py``-style relpath.

    Stored paths look like ``/…/study_repos/corpus/<repo_id>/cli/holon.py``. We keep
    everything after ``corpus/<repo_id>/`` and normalize separators.
    """
    if not path:
        return None
    p = path.replace("\\", "/").lstrip("/")
    if repo_id:
        marker = f"corpus/{repo_id}/"
        idx = p.find(marker)
        if idx >= 0:
            p = p[idx + len(marker):]
    return p.rstrip("/") or None


def github_url_for(repo: dict | None, name: str, rel_path: str | None, line: int | None) -> str | None:
    """Commit-pinned GitHub blob URL for one occurrence (deterministic, reproducible)."""
    sha = repo.get("commit_sha") if isinstance(repo, dict) else None
    if not sha or not rel_path:
        return None
    owner_repo = str(name).replace("__", "/")
    if "/" not in owner_repo:
        return None
    base = f"https://github.com/{owner_repo}/blob/{sha}/{rel_path}"
    return f"{base}#L{line}" if line else base


def node_lists(report: dict) -> list[tuple[str, list[dict], str]]:
    """Yield ``(construct_id, nodes, file_path)`` for every construct node in the report.

    The tuple includes the per-file path (from ``file_details``) so that an
    occurrence can later carry its exact ``file`` + commit-pinned GitHub URL.
    """
    fd = report.get("file_details", [])
    mapping = [
        ("C1", "depends_calls"),
        ("C2", "security_calls"),
        ("C3", "annotated_depends"),
        ("C4", "yield_functions"),
    ]
    out: list[tuple[str, list[dict], str]] = []
    for cid, key in mapping:
        for fr in fd:
            nodes: list[dict] = []
            for n in fr.get(key, []):
                nodes.append(dict(n))
            if nodes:
                out.append((cid, nodes, fr.get("path") or ""))
    return out


def collect_occurrences(reports_dir: Path | None = None) -> list[dict]:
    """Flatten every construct occurrence across all reports into canonical nodes."""
    reports_dir = reports_dir or REPORTS_DIR
    occurrences: list[dict] = []
    for path in sorted(reports_dir.glob("*.json")):
        if path.name.startswith("."):
            continue
        try:
            report = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        repo = report.get("repo") if isinstance(report.get("repo"), dict) else None
        name = repo.get("name") if repo else None
        display = repo.get("full_name") or name or path.stem.replace("__", "/")
        for cid, nodes, fpath in node_lists(report):
            rel = _rel_file_path(fpath, name)
            for n in nodes:
                url = github_url_for(repo, str(display), rel, n.get("line"))
                occurrences.append(
                    _node_occurrence(str(display), n, cid, file=rel or None, github_url=url or None)
                )
    return occurrences


def group_fingerprints(occurrences: list[dict], examples_per: int = EXAMPLES_PER_FP) -> list[dict]:
    """Dedupe occurrences by canonical fingerprint; keep counts and code examples."""
    groups: dict[str, dict] = {}
    for occ in occurrences:
        fp = occ["fingerprint"]
        g = groups.setdefault(fp, {"construct": occ["construct"], "fingerprint": fp,
                                   "total_occurrences": 0, "repos": set(), "examples": []})
        g["total_occurrences"] += 1
        g["repos"].add(occ["repo"])
        if len(g["examples"]) < examples_per:
            g["examples"].append(
                {k: v for k, v in occ.items() if k not in ("repo", "line") and v is not None}
                | {"repo": occ["repo"], "line": occ["line"]}
            )
    for g in groups.values():
        g["repos"] = sorted(g["repos"])
    return sorted(groups.values(), key=lambda g: (g["construct"], g["fingerprint"]))


def build_fingerprints(reports_dir: Path | None = None, out_dir: Path | None = None) -> list[dict]:
    """Full pipeline: reports -> occurrences -> grouped fingerprints -> JSON.

    Returns the grouped fingerprint list; additionally writes
    ``novelty_fingerprints.json`` (metadata + groups) and
    ``novelty_occurrences.json`` (raw flattened list) under ``out_dir``.
    """
    occurrences = collect_occurrences(reports_dir)
    groups = group_fingerprints(occurrences)
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "novelty_occurrences.json").write_text(
            json.dumps(occurrences, indent=2))
        (out_dir / "novelty_fingerprints.json").write_text(
            json.dumps({
                "schema_version": "0.1",
                "source_reports": str(reports_dir or REPORTS_DIR),
                "total_occurrences": len(occurrences),
                "distinct_fingerprints": len(groups),
                "fingerprints": groups,
            }, indent=2))
    return groups


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Build canonical DI fingerprints from reports")
    ap.add_argument("--reports", default=None, help="reports dir (default corpus/reports)")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "out"))
    args = ap.parse_args()
    groups = build_fingerprints(Path(args.reports) if args.reports else None, Path(args.out))
    print(f"[fingerprints] {sum(g['total_occurrences'] for g in groups)} occurrences"
          f" -> {len(groups)} distinct fingerprints")
    for g in groups:
        print(f"  {g['construct']:>3} {g['fingerprint']:<42} n={g['total_occurrences']}")