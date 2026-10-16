#!/usr/bin/env python3
"""analysis/ai_review_scan.py — an independent S1-S4 pass over the 280 reviewed
repositories, done from the code itself rather than from the AST parser's verdict.

This is a *review aid*, not the parser: it re-derives the evidence with its own
rules so the resulting labels are an independent judgement (as a human reviewer
would give), then the rare S3/S4 candidates are meant to be hand-checked.

Signals are collected over production files only (test files excluded). The
label follows the rubric in docs/s1s4_reviewer_rubric.md:
    S4 > S2 > S3 > S1
where S3 includes ambient/request-state providers that are actually called,
local Depends/Security aliases, the Fowler constructor/setter/interface forms,
attribute injection, and service-locator lookups.

Usage:
    .venv/bin/python analysis/ai_review_scan.py --out analysis/out/ai_review_scan.csv
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "study_repos" / "corpus"
MERGED = ROOT / "review_results" / "merged" / "per_repo_labels.json"

EXTERNAL_DI_LIBS = {
    "aioinject", "antidote", "asgi_container", "asyncdi", "cervantes",
    "decopatch", "dependency_injector", "di", "dishka", "fastapi_injector",
    "flask_injector", "fluid", "inject", "injector", "ioccontainer", "ioclib",
    "kani", "kink", "lagom", "morango", "punq", "pyioc",
    "python_dependency_injector", "servicemanager", "solitary", "svc", "svcs",
    "thiriy", "wired", "wireup",
}
AMBIGUOUS = {"injector", "servicemanager"}
STRICT_TOKENS = {"multiprovider", "singleton", "ConstructorBinder",
                 "get_injector", "MethodCaller", "AutoBind"}
DI_API_TOKENS = {
    "dependency_injector": {"containers", "DeclarativeContainer", "providers",
                            "Provider", "wire", "inject", "Configuration",
                            "Singleton", "Factory", "Resource"},
    "dishka": {"Dishka", "make_async_container", "make_container", "FromDishka",
               "AnyOf", "provide"},
    "injector": {"Injector", "inject", "multiprovider", "singleton", "provide"},
    "servicemanager": {"ServiceManager", "register", "resolve", "get_service"},
    "ioccontainer": {"Container", "Configuration", "Factory", "Singleton"},
    "punq": {"Punq", "Container", "register", "resolve"},
    "kani": {"Kani", "Component", "inject", "provide"},
    "wired": {"registry", "inject", "container", "providers"},
    "wireup": {"wire", "container", "ServiceContainer", "inject"},
}
DI_TOKENLESS = EXTERNAL_DI_LIBS - set(DI_API_TOKENS)

TEST_SEGMENTS = {"test", "tests", "testing", "__tests__", "spec", "specs"}
NON_PROD_SEGMENTS = {"docs", "doc", "documentation", "archive", "archives",
                     "examples", "example", "samples", "sandbox"}
RE_DEPENDS = re.compile(r"\bDepends\s*\(")
RE_SECURITY = re.compile(r"\bSecurity\s*\(")
RE_ANNOTATED = re.compile(r"Annotated\s*\[[^\]]*\b(Depends|Security)\b")
RE_IMPORT = re.compile(r"^\s*(?:from\s+([\w\.]+)\s+import\s+(.+)|import\s+(.+))",
                       re.MULTILINE)
RE_LOCAL_DEPENDS = re.compile(
    r"^\s*from\s+\.+[\w\.]*\s+import\s+[^\n]*\b(Depends|Security)\b", re.MULTILINE)


def is_production(path: Path) -> bool:
    parts = set(path.parts)
    if parts & TEST_SEGMENTS:
        return False
    if any(p in NON_PROD_SEGMENTS or p.startswith("docs-backup") for p in path.parts):
        return False
    name = path.name
    if name == "conftest.py" or name.startswith("test_") or name.endswith("_test.py"):
        return False
    if any(p in {"site-packages", ".venv", "venv", "node_modules", ".git"} for p in path.parts):
        return False
    return path.suffix == ".py"


def py_files(repo_dir: Path) -> list[Path]:
    out: list[Path] = []
    skip = {"site-packages", ".venv", "venv", "node_modules", ".git", ".tox",
            ".mypy_cache", ".pytest_cache", "__pycache__", "build", "dist",
            ".eggs"}
    for dirpath, dirnames, filenames in os.walk(repo_dir):
        dirnames[:] = [d for d in dirnames if d not in skip and not d.endswith(".egg-info")]
        for fn in filenames:
            if fn.endswith(".py"):
                p = Path(dirpath) / fn
                if is_production(p):
                    out.append(p)
        if len(out) > 1500:
            break
    return out


def _is_ambient(node: ast.AST) -> bool:
    """True for request.state / app.state / websocket.state / request.app.state."""
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and n.attr == "state":
            v = n.value
            if isinstance(v, ast.Name) and v.id in {"request", "app", "websocket"}:
                return True
            if (isinstance(v, ast.Attribute) and v.attr == "app"
                    and isinstance(v.value, ast.Name)
                    and v.value.id in {"request", "websocket"}):
                return True
    return False


def _parse(src: str):
    """ast.parse that ignores SyntaxWarning from invalid escapes in cloned repos."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(src)


def func_returns_state(src: str) -> set[str]:
    """Module/class-level defs whose body returns framework ambient state."""
    names: set[str] = set()
    try:
        tree = _parse(src)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Return) and sub.value is not None \
                        and _is_ambient(sub.value):
                    names.add(node.name)
    return names


_RE_LOCATOR_CALL = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*(get|resolve|provide|lookup|locate|inject)\s*\(")
_LOCATOR_TOKEN = re.compile(r"([Cc]ontainer|[Rr]egistry|[Ii]njector|[Ll]ocator)$")


def locator_hits(src: str) -> bool:
    """A service-locator call: <registryish>.resolve/get(...). Excludes plain
    dicts used as data ('by_' groupings, *_catalog, ALL_CAPS constants)."""
    for m in _RE_LOCATOR_CALL.finditer(src):
        recv = m.group(1)
        if not _LOCATOR_TOKEN.search(recv):
            continue
        low = recv.lower()
        if "by_" in low or low.endswith("_catalog") or recv.isupper():
            continue
        return True
    return False


def _capwords(expr: ast.AST) -> bool:
    if isinstance(expr, ast.Name):
        return expr.id[:1].isupper()
    if isinstance(expr, ast.Attribute):
        return expr.attr[:1].isupper()
    return False


def ctor_classes(src: str) -> set[str]:
    """Class names that receive a collaborator, store it on self, and invoke it
    as a service (self.attr(...) or self.attr.method(...))."""
    found: set[str] = set()
    try:
        tree = _parse(src)
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == "__init__"):
                continue
            params = {a.arg for a in item.args.args} - {"self"}
            stored = {t.attr for stmt in ast.walk(item) if isinstance(stmt, ast.Assign)
                      for t in stmt.targets
                      if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                      and t.value.id == "self"
                      and isinstance(stmt.value, ast.Name) and stmt.value.id in params}
            if not stored:
                continue
            for c in ast.walk(node):
                if not isinstance(c, ast.Call):
                    continue
                f = c.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                        and f.value.id == "self" and f.attr in stored:
                    found.add(node.name)
                    break
                if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Attribute)
                        and isinstance(f.value.value, ast.Name)
                        and f.value.value.id == "self" and f.value.attr in stored):
                    found.add(node.name)
                    break
    return found


def ctor_callsite(src: str, classes: set[str]) -> bool:
    """A call to one of the injection classes passing a collaborator (a name, or
    a CapWords construction) rather than only literals."""
    if not classes:
        return False
    try:
        tree = _parse(src)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in classes:
            for a in node.args:
                if isinstance(a, ast.Name):
                    return True
                if isinstance(a, ast.Call) and isinstance(a.func, ast.Name):
                    return True
    return False


def scan_repo(repo_dir: Path) -> dict:
    ev = {
        "depends": 0, "security": 0, "annotated": 0, "yield_dep": 0,
        "containers": set(), "container_used": False, "ambient": 0,
        "local_alias": 0, "ctor": False, "setter": False,
        "service_locator": 0, "evidence": [],
    }
    files: list[tuple[str, str]] = []
    for f in py_files(repo_dir):
        try:
            src = f.read_text(errors="ignore")
        except OSError:
            continue
        files.append((str(f.relative_to(repo_dir)), src))
    blob_all = "".join(src for _, src in files)
    for rel, src in files:
        if RE_DEPENDS.search(src):
            ev["depends"] += len(RE_DEPENDS.findall(src))
            if not any("Depends" in e for e in ev["evidence"]):
                ev["evidence"].append(f"Depends in {rel}")
        if RE_SECURITY.search(src):
            ev["security"] += len(RE_SECURITY.findall(src))
        if RE_ANNOTATED.search(src):
            ev["annotated"] += 1
        # container imports
        for m in RE_IMPORT.finditer(src):
            mod = (m.group(1) or m.group(3) or "").split(".")[0]
            if mod in EXTERNAL_DI_LIBS:
                ev["containers"].add(mod)
        # yield dependency
        try:
            tree = _parse(src)
        except SyntaxError:
            tree = None
        if tree is not None:
            gen_funcs = {n.name for n in ast.walk(tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and any(isinstance(s, ast.Yield) for s in ast.walk(n))}
            if gen_funcs:
                for d in re.findall(r"Depends\s*\(\s*(\w+)", src):
                    if d in gen_funcs:
                        ev["yield_dep"] += 1
        # ambient state provider, called elsewhere
        provs = func_returns_state(src)
        for pname in provs:
            if re.search(rf"\b{re.escape(pname)}\s*\(", src) and pname not in {"__init__"}:
                ev["ambient"] += 1
        if provs:
            ev["evidence"].append(f"ambient provider {sorted(provs)} in {rel}")
        if RE_LOCAL_DEPENDS.search(src):
            ev["local_alias"] += 1
            ev["evidence"].append(f"local Depends alias in {rel}")
        if locator_hits(src):
            ev["service_locator"] += 1
            ev["evidence"].append(f"locator in {rel}")
    # repo-wide constructor injection: gather classes then find call sites
    all_ctor: set[str] = set()
    for _, src in files:
        all_ctor |= ctor_classes(src)
    if all_ctor and any(ctor_callsite(src, all_ctor) for _, src in files):
        ev["ctor"] = True
        ev["evidence"].append(f"ctor injection {sorted(all_ctor)[:5]}")
    # container usage gate
    used = False
    for lib in ev["containers"]:
        if lib in AMBIGUOUS:
            if re.search(r"@\s*inject\b|\b(inject|multiprovider|singleton)\b", blob_all):
                used = True
        elif lib in DI_API_TOKENS:
            if any(tok in blob_all for tok in DI_API_TOKENS[lib]):
                used = True
        elif lib in DI_TOKENLESS:
            used = True
    ev["container_used"] = used
    return ev


def label(ev: dict) -> str:
    if ev["containers"] and ev["container_used"]:
        return "S4"
    if ev["depends"] or ev["security"] or ev["annotated"]:
        return "S2"
    if any([ev["ambient"], ev["local_alias"], ev["ctor"], ev["setter"],
            ev["service_locator"]]):
        return "S3"
    return "S1"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="analysis/out/ai_review_scan.csv")
    args = ap.parse_args()
    rows = json.loads(MERGED.read_text())["rows"]
    out = []
    for r in rows:
        repo = r["repo_canonical"]
        d = CORPUS / repo.replace("/", "__")
        ev = scan_repo(d) if d.exists() else {}
        lab = label(ev) if ev else "?"
        out.append({
            "arm": r["arm"], "repo": repo, "commit": r["commit"],
            "ai_label": lab, "ast_verdict": r["ast_verdict"],
            "depends": ev.get("depends"), "security": ev.get("security"),
            "annotated": ev.get("annotated"), "yield_dep": ev.get("yield_dep"),
            "containers": ",".join(sorted(ev.get("containers", []))),
            "container_used": ev.get("container_used"),
            "ambient": ev.get("ambient"), "local_alias": ev.get("local_alias"),
            "ctor": ev.get("ctor"), "service_locator": ev.get("service_locator"),
            "evidence": "; ".join(ev.get("evidence", [])[:6]),
        })
    outp = ROOT / args.out
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print("wrote", outp.relative_to(ROOT))
    print("ai_label:", dict(Counter(o["ai_label"] for o in out)))
    print("ast     :", dict(Counter(o["ast_verdict"] for o in out)))


if __name__ == "__main__":
    main()
