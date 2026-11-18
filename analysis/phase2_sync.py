"""Phase 2: execution mode of corpus dependencies (local only)."""
from __future__ import annotations
import ast, json, glob, os, random, statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "corpus" / "reports_v0.5"
REPOS = ROOT / "study_repos" / "corpus"

def resolve_async(repo: str, target_name: str, target_file: str) -> tuple[bool | None, int]:
    """Return (is_async, n_defs_with_name) for target_name in target_file."""
    repo_dir = REPOS / repo.replace("/", "__")
    # target_file may be relative or absolute
    if os.path.isabs(target_file):
        path = Path(target_file)
    else:
        path = repo_dir / target_file
    if not path.exists():
        return None, 0
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None, 0
    defs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == target_name:
                defs.append(isinstance(node, ast.AsyncFunctionDef))
    if not defs:
        return None, 0
    # name collision: if more than one def with same name, ambiguous
    return defs[0], len(defs)

def main():
    repos = sorted(REPORTS.glob("*.json"))
    total_edges = 0
    resolved_edges = 0
    unresolved_args = 0
    # per-repo
    repo_stats = []  # list of dict
    # name collision sensitivity
    single_def_edges = 0
    single_def_sync = 0
    # blocking heuristic targets
    blocking_hits = 0
    sync_edges_total = 0

    for i, rp in enumerate(repos):
        if i % 100 == 0:
            print(f"progress {i}/{len(repos)}", flush=True)
        d = json.load(open(rp))
        repo = d["repo"]["name"]
        g = d["dependency_graph"]
        edges = g.get("edges", [])
        unresolved = g.get("unresolved_depends", 0)
        unresolved_args += unresolved
        n_edges = len(edges)
        total_edges += n_edges
        # per-repo
        repo_sync = 0
        repo_total = 0
        repo_has_sync = False
        # name collision: count distinct target names defined once
        # First pass: gather defs per name in repo? too heavy; do per-target
        for e in edges:
            total_edges  # already
            resolved_edges += 1
            target = e["target"]
            tfile = e["target_file"]
            is_async, n_defs = resolve_async(repo, target, tfile)
            repo_total += 1
            if is_async is None:
                # unresolved edge (shouldn't happen if in edges list, but skip)
                continue
            if not is_async:
                repo_sync += 1
                repo_has_sync = True
                sync_edges_total += 1
            # name collision sensitivity
            if n_defs == 1:
                single_def_edges += 1
                if not is_async:
                    single_def_sync += 1
        repo_stats.append({
            "repo": repo,
            "n_edges": repo_total,
            "n_sync": repo_sync,
            "has_sync": repo_has_sync,
            "sync_share": (repo_sync / repo_total) if repo_total else 0.0,
        })

    # aggregate
    n_repos = len(repo_stats)
    graph_bearing = [r for r in repo_stats if r["n_edges"] > 0]
    n_gb = len(graph_bearing)
    repos_with_sync = sum(1 for r in graph_bearing if r["has_sync"])
    repo_prevalence = repos_with_sync / n_gb if n_gb else 0
    median_sync_share = statistics.median(r["sync_share"] for r in graph_bearing) if graph_bearing else 0
    overall_sync_share = sync_edges_total / resolved_edges if resolved_edges else 0
    print("=== Phase 2.1 resolution rate ===")
    print(f"resolved edges: {resolved_edges}, unresolved args: {unresolved_args}, total args: {resolved_edges+unresolved_args}")
    print(f"resolution rate: {resolved_edges/(resolved_edges+unresolved_args):.4f}")
    print("=== Phase 2.2 repo-level prevalence ===")
    print(f"graph-bearing repos: {n_gb}")
    print(f"repos with >=1 sync target: {repos_with_sync} ({repo_prevalence:.4f})")
    print(f"per-repo median sync share: {median_sync_share:.4f}")
    print(f"overall sync edge share: {overall_sync_share:.4f} (edges {sync_edges_total}/{resolved_edges})")
    print("=== Phase 2.3 name-collision sensitivity ===")
    print(f"single-def edges: {single_def_edges}, sync among them: {single_def_sync} ({single_def_sync/single_def_edges:.4f})")

    # bootstrap CI for repo prevalence and median sync share (resample repos)
    random.seed(20261103)
    B = 2000
    prev_boot = []
    med_boot = []
    for _ in range(B):
        sample = [random.choice(graph_bearing) for _ in range(n_gb)]
        prev_boot.append(sum(1 for r in sample if r["has_sync"]) / n_gb)
        med_boot.append(statistics.median(r["sync_share"] for r in sample))
    prev_boot.sort(); med_boot.sort()
    print(f"repo prevalence 95% CI: [{prev_boot[int(0.025*B)]: .4f}, {prev_boot[int(0.975*B)] :.4f}]")
    print(f"median sync share 95% CI: [{med_boot[int(0.025*B)] :.4f}, {med_boot[int(0.975*B)] :.4f}]")

    # save per-repo stats
    import csv
    out = ROOT / "analysis" / "out" / "phase2_repo_sync.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["repo","n_edges","n_sync","has_sync","sync_share"])
        w.writeheader()
        for r in repo_stats:
            w.writerow(r)
    print("wrote", out)

    # blocking heuristic: count sync targets whose body (or 1-level callees) use known blocking I/O
    BLOCKING = {"requests", "urllib", "httpx" }  # httpx sync client; crude
    # We'll do a simpler text heuristic: grep target function body for blocking calls
    blocking_count = 0
    sync_targets_seen = 0
    for i, rp in enumerate(repos):
        if i % 100 == 0:
            print(f"progress {i}/{len(repos)}", flush=True)
        d = json.load(open(rp))
        repo = d["repo"]["name"]
        repo_dir = REPOS / repo.replace("/", "__")
        g = d["dependency_graph"]
        for e in g.get("edges", []):
            target = e["target"]; tfile = e["target_file"]
            is_async, n_defs = resolve_async(repo, target, tfile)
            if is_async is not False:
                continue
            sync_targets_seen += 1
            # read file, find function, check body text
            path = (REPOS / repo.replace("/", "__") / tfile) if not os.path.isabs(tfile) else Path(tfile)
            if not path.exists():
                continue
            src = path.read_text(encoding="utf-8", errors="replace")
            # extract function body via ast
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == target:
                    # get source segment
                    seg = ast.get_source_segment(src, node) or ""
                    low = seg.lower()
                    if any(tok in low for tok in ["requests.", "urllib.", "psycopg2", "pymongo", "time.sleep", "open(", ".execute(", "session.", "engine.", "create_engine", "sessionmaker"]):
                        blocking_count += 1
    print("=== Phase 2.4 blocking heuristic (coarse) ===")
    print(f"sync targets inspected: {sync_targets_seen}, flagged blocking: {blocking_count} ({blocking_count/sync_targets_seen:.4f})")
    print("Note: heuristic is keyword-based; manual validation on 100 targets still required.")

if __name__ == "__main__":
    main()