"""
analysis/ast_quality.py — Phase 2A: static quality/complexity metrics per repo.

Runs an AST pass over the *accepted* clones (study_repos/corpus/<owner>__<repo>)
to measure maintainability proxies for each repo:

  - mean function length (lines of code per function/body)
  - branch density (if/for/while/try/except/with/ternary per function)
  - type-annotation share (% of functions with any annotation)
  - docstring coverage (% of functions/modules/classes with a docstring)
  - imports per file (coupling proxy)

Only production files (source), excluding test paths and __pycache__ / vendored
dirs, mirroring the report extractor's notion of production scope as closely as
is cheap. Output: analysis/out/ast_quality.csv (one row per accepted repo).

No network. Reads local clones.
"""

from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
CORPUS_DIR = ROOT.parent / "study_repos" / "corpus"
MANIFEST = ROOT.parent / "corpus" / "manifest.json"

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "venv", "env",
             "migrations", "alembic", ".tox", "dist", "build", "site-packages",
             ".pytest_cache", ".mypy_cache", ".ruff_cache", "tests", "test"}
SKIP_SUFFIXES = (".pyc", ".pyo", ".pyd")

TEST_NAMES = {"test", "tests", "testing", "conftest"}


def _is_production(path: Path, rel: Path) -> bool:
    for part in rel.parts:
        if part in SKIP_DIRS or part.lower() in TEST_NAMES:
            return False
    return True


def _metrics_for_file(text: str) -> dict:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    n_funcs = 0
    src_lines = text.splitlines()
    total_branch = 0
    doc_funcs = 0
    ann_funcs = 0
    annotated_args = 0
    total_args = 0
    total_body_lines = 0

    def _branch_count(node) -> int:
        b = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp, ast.For, ast.While,
                                  ast.Try, ast.ExceptHandler, ast.With,
                                  ast.comprehension, ast.Assert, ast.Match)):
                b += 1
        return b

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            n_funcs += 1
            body_lines = (node.end_lineno or 0) - (node.lineno or 0) + 1
            total_body_lines += body_lines
            total_branch += _branch_count(node)
            if ast.get_docstring(node):
                doc_funcs += 1
            # annotations
            has_ret = bool(node.returns)
            has_args = any(
                (a.annotation or (a.type_comment)) for a in node.args.args
            )
            if has_ret or has_args:
                ann_funcs += 1
            total_args += len(node.args.args)
            annotated_args += sum(1 for a in node.args.args if a.annotation)

    module_doc = bool(ast.get_docstring(tree))
    class_docs = sum(1 for c in ast.walk(tree) if isinstance(c, ast.ClassDef)
                     and ast.get_docstring(c))
    n_classes = sum(1 for c in ast.walk(tree) if isinstance(c, ast.ClassDef))
    n_imports = sum(1 for n in ast.walk(tree)
                    if isinstance(n, (ast.Import, ast.ImportFrom)))

    return {
        "n_funcs": n_funcs,
        "body_lines": total_body_lines,
        "tot_branch": total_branch,
        "doc_funcs": doc_funcs,
        "ann_funcs": ann_funcs,
        "tot_args": total_args,
        "ann_args": annotated_args,
        "n_classes": n_classes,
        "class_doc": class_docs,
        "module_doc": int(module_doc),
        "n_imports": n_imports,
    }


def main() -> None:
    import json
    manifest = json.loads(MANIFEST.read_text())
    accepted = [a["full_name"] for a in manifest["accepted"]]

    rows = []
    for full in accepted:
        d = CORPUS_DIR / full.replace("/", "__")
        agg = {"n_files": 0, "n_funcs": 0, "body_lines": 0, "tot_branch": 0,
               "doc_funcs": 0, "ann_funcs": 0, "tot_args": 0, "ann_args": 0,
               "n_classes": 0, "class_doc": 0, "module_doc": 0, "n_imports": 0,
               "curly": None}
        if not d.is_dir():
            rows.append({**{"repo": full}, **_blank(agg)})
            continue
        for p in d.rglob("*.py"):
            if p.suffix in SKIP_SUFFIXES:
                continue
            rel = p.relative_to(d)
            if not _is_production(p, rel):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            m = _metrics_for_file(text)
            if not m:
                continue
            agg["n_files"] += 1
            for k in ("n_funcs", "body_lines", "tot_branch", "doc_funcs",
                      "ann_funcs", "tot_args", "ann_args", "n_classes",
                      "class_doc", "module_doc", "n_imports"):
                agg[k] += m[k]

        rows.append({**{"repo": full}, **_blank(agg)})

    rows.sort(key=lambda r: r["repo"])
    with (OUT_DIR / "ast_quality.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["repo", "n_files", "n_funcs",
                                           "mean_func_len", "mean_branch_per_func",
                                           "type_ann_share", "docstring_share",
                                           "arg_ann_share", "class_doc_share",
                                           "imports_per_file"])
        w.writeheader()
        for r in rows:
            w.writerow(_derived(r))

    cov = sum(1 for r in rows if r["n_files"] > 0)
    n = len(rows)
    print(f"[ast_quality] {n} repos; {cov} ({round(100*cov/max(n,1),1)}%) with "
          f">=1 production .py; wrote analysis/out/ast_quality.csv")


def _blank(agg: dict) -> dict:
    out = dict(agg)
    out["curly"] = None
    return out


def _derived(r: dict) -> dict:
    nf = max(r["n_funcs"], 1)
    nfile = max(r["n_files"], 1)
    ncls = max(r["n_classes"], 1)
    return {
        "repo": r["repo"],
        "n_files": r["n_files"],
        "n_funcs": r["n_funcs"],
        "mean_func_len": round(r["body_lines"] / nf, 2),
        "mean_branch_per_func": round(r["tot_branch"] / nf, 3),
        "type_ann_share": round(100 * r["ann_funcs"] / nf, 1),
        "docstring_share": round(100 * r["doc_funcs"] / nf, 1),
        "arg_ann_share": round(100 * r["ann_args"] / max(r["tot_args"], 1), 1),
        "class_doc_share": round(100 * r["class_doc"] / ncls, 1),
        "imports_per_file": round(r["n_imports"] / nfile, 2),
    }


if __name__ == "__main__":
    main()
