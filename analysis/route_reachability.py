"""Phase 2 (extension): route-reachability cut for sync dependency prevalence.

For each repo, keep only dependency edges whose source function is reachable
from a FastAPI route handler (directly or via sub-dependencies). Recompute
the sync edge share and repo-level "any sync target on a hot path" prevalence.
"""
from __future__ import annotations
import ast, json, os, random, statistics
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "corpus" / "reports_v0.5"
REPOS = ROOT / "study_repos" / "corpus"

ROUTE_DECORATORS = {"get","post","put","patch","delete","options","head","api_route","route"}
ROUTE_CALLS = {"add_api_route", "add_api_websocket_route"}

def is_route_decorator(dec) -> bool:
    # @app.get(...), @router.post(...), @app.api_route(...)
    if isinstance(dec, ast.Call):
        func = dec.func
    else:
        func = dec
    if isinstance(func, ast.Attribute) and func.attr in ROUTE_DECORATORS:
        return True
    return False

def find_route_handlers(repo_dir: Path) -> set[str]:
    handlers = set()
    count = 0
    for py in repo_dir.rglob("*.py"):
        if any(part in {".venv","venv","node_modules","__pycache__",".git","dist","build"} for part in py.parts):
            continue
        count += 1
        if count > 1500:
            break
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(is_route_decorator(d) for d in node.decorator_list):
                    handlers.add(node.name)
            # add_api_route("/path", handler)
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
                if name in ROUTE_CALLS and len(node.args) >= 2:
                    arg = node.args[1]
                    if isinstance(arg, ast.Name):
                        handlers.add(arg.id)
                    elif isinstance(arg, ast.Attribute):
                        handlers.add(arg.attr)
    return handlers

def resolve_async(repo: str, target_name: str, target_file: str):
    repo_dir = REPOS / repo.replace("/", "__")
    path = (repo_dir / target_file) if not os.path.isabs(target_file) else Path(target_file)
    if not path.exists():
        return None, 0
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None, 0
    defs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == target_name:
            defs.append(isinstance(node, ast.AsyncFunctionDef))
    if not defs:
        return None, 0
    return defs[0], len(defs)

def main():
    repos = sorted(REPORTS.glob("*.json"))
    total_edges = 0
    route_edges = 0
    route_sync = 0
    repo_stats = []
    n_repos_with_route = 0
    n_repos_with_route_sync = 0
    for i, rp in enumerate(repos):
        if i % 50 == 0:
            print(f"progress {i}/{len(repos)}", flush=True)
        d = json.load(open(rp))
        repo = d["repo"]["name"]
        repo_dir = REPOS / repo.replace("/", "__")
        if i % 1 == 0:
            pass
        handlers = find_route_handlers(repo_dir) if repo_dir.exists() else set()
        g = d["dependency_graph"]
        edges = g.get("edges", [])
        # build adjacency source->targets
        adj = defaultdict(set)
        for e in edges:
            adj[e["source"]].add(e["target"])  # not used for reachability via target name only; need edge-level
        # reachable sources: BFS from handlers following edges (source->target)
        # edges: source depends on target. Reachable set of functions.
        # adjacency by source function -> list of (target function name)
        adj2 = defaultdict(set)
        for e in edges:
            adj2[e["source"]].add(e["target"])
        reachable = set(handlers)
        q = deque(handlers)
        while q:
            cur = q.popleft()
            for t in adj2.get(cur, ()):
                if t not in reachable:
                    reachable.add(t)
                    q.append(t)
        # classify edges
        repo_total = 0
        repo_sync = 0
        repo_has_route = bool(handlers)
        repo_has_route_sync = False
        for e in edges:
            total_edges += 1
            if e["source"] not in reachable:
                continue
            route_edges += 1
            repo_total += 1
            is_async, nd = resolve_async(repo, e["target"], e["target_file"])
            if is_async is None:
                continue
            if not is_async:
                route_sync += 1
                repo_sync += 1
                repo_has_route_sync = True
        if repo_has_route:
            n_repos_with_route += 1
        if repo_has_route_sync:
            n_repos_with_route_sync += 1
        repo_stats.append({
            "repo": repo, "n_handlers": len(handlers), "n_route_edges": repo_total,
            "n_route_sync": repo_sync, "has_route_sync": repo_has_route_sync,
        })

    print("=== Route-reachability results ===")
    print(f"repos: {len(repos)}, with >=1 route handler: {n_repos_with_route}")
    print(f"total edges: {total_edges}, route-reachable edges: {route_edges} ({route_edges/total_edges:.4f})")
    print(f"route-reachable sync edges: {route_sync} ({route_sync/route_edges:.4f})")
    print(f"repos with route-reachable sync target: {n_repos_with_route_sync} / {n_repos_with_route} = {n_repos_with_route_sync/n_repos_with_route:.4f}")
    print(f"repos with route-reachable sync target / all repos: {n_repos_with_route_sync}/{len(repos)} = {n_repos_with_route_sync/len(repos):.4f}")

    # bootstrap CI for repo prevalence (resample repos that have route handlers)
    rb = [r for r in repo_stats if r["n_handlers"] > 0]
    random.seed(20261117)
    B = 2000
    boot = []
    for _ in range(B):
        samp = [random.choice(rb) for _ in range(len(rb))]
        boot.append(sum(1 for r in samp if r["has_route_sync"]) / len(rb))
    boot.sort()
    print(f"route-reachable sync repo prevalence 95% CI: [{boot[int(.025*B)]:.4f}, {boot[int(.975*B)]:.4f}]")

    import csv
    out = ROOT / "analysis" / "out" / "phase2_route_reachability.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(repo_stats[0].keys()))
        w.writeheader()
        w.writerows(repo_stats)
    print("wrote", out)

if __name__ == "__main__":
    main()