"""
analysis/rq3_depth_tail.py - RQ3 deep-tail analysis: repos whose DI graph
contains a long Depends-of-Depends chain.

The RQ3 headline is "shallow + fan-out": median graph depth 2, IQR 2-3, with
shared hubs reused across many handlers. This script characterises the deep
tail of the depth distribution (max_depth >= 5) on the full 2,179-repo census,
so we can say whether genuine deep chains exist, how they are structured, and
whether they are just large fan-out hubs seen edge-on.

Consumes the same artifacts as aggregate.py (no network, no re-cloning).

Outputs analysis/out/rq3_depth_tail.csv and writes a summary to stdout.

Usage:
    uv run python analysis/rq3_depth_tail.py
"""

from __future__ import annotations

import collections
import csv
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
REPORTS_DIR = ROOT.parent / "corpus" / "reports"
MANIFEST_PATH = ROOT.parent / "corpus" / "manifest.json"
DEPTH_CUTOFF = 5


def load_accepted() -> list[dict]:
    with open(MANIFEST_PATH) as f:
        return json.load(f)["accepted"]


def missed_edges(edges: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split edges into those with clean source+target vs. any referencing a
    junk 'file:line' / path-bearing node (mirrors split_edges)."""
    clean, junk = [], []
    for e in edges:
        s, t = str(e.get("source", "")), str(e.get("target", ""))
        if "/" in s or ":" in s or "/" in t or ":" in t:
            junk.append(e)
        else:
            clean.append(e)
    return clean, junk


def longest_callable_chains(md: dict) -> list[list[str]]:
    """Return the longest root->leaf callable chains in the clean graph.

    Uses only nodes whose id is a callable name (no path separator / 'file:line'),
    and only edges whose source+target are both callable names. Returns all
    chains at the maximum depth found (empty list if the graph is empty).
    """
    edges = md.get("edges") or []
    clean_nodes = {n["id"] for n in (md.get("nodes") or []) if "/" not in n["id"] and ":" not in n["id"]}
    children: dict[str, list[str]] = collections.defaultdict(list)
    targets: set[str] = set()
    for s, t in ((e.get("source"), e.get("target")) for e in edges):
        if s in clean_nodes and t in clean_nodes:
            children[s].append(t)
            targets.add(t)
    roots = [n for n in children if n not in targets]
    if not roots or not clean_nodes:
        return []

    best: list[list[str]] = []

    def dfs(node: str, path: list[str], visited: set[str]) -> None:
        if node not in children or not children[node]:
            if len(path) > len(best[-1]) if best else True:
                best.clear()
                best.append(list(path))
            elif best and len(path) == len(best[-1]):
                best.append(list(path))
            return
        for child in children[node]:
            if child not in visited:
                dfs(child, path + [child], visited | {child})

    for root in roots:
        dfs(root, [root], {root})
    return best


def main() -> None:
    accepted = load_accepted()
    rows = []
    tail: list[dict] = []
    gb = 0  # graph-bearing accepted repos
    depth_hist: collections.Counter = collections.Counter()

    unresolved_deep_share: list[float] = []          # unresolved_pct among tail
    nodes_clean_tail: list[int] = []
    edges_clean_tail: list[int] = []
    depth_of_tail: list[int] = []
    longest_chain_len: list[int] = []
    fanout_hub_tail = 0
    fork_or_archived_tail = 0  # repo is fork/archived (from manifest)

    for a in accepted:
        name = a["full_name"]
        p = REPORTS_DIR / f"{name.replace('/', '__')}.json"
        if not p.exists():
            continue
        rep = json.loads(p.read_text())
        g = rep.get("dependency_graph") or {}
        nodes = g.get("nodes") or []
        if not nodes:
            continue
        gb += 1

        raw_n = len(nodes)
        clean_edges, junk_edges = missed_edges(g.get("edges") or [])
        # unresolved = edges that never resolve inside the graph (kept as
        # raw figure in reports as unresolved_depends)
        unresolved = g.get("unresolved_depends", 0)
        depth = int(g.get("max_depth") or 0)
        depth_hist[depth] += 1

        # fan-out: does some clean node have >=3 dependents (clean edge count)?
        indeg: collections.Counter = collections.Counter()
        for e in clean_edges:
            indeg[e["target"]] += 1
        has_hub = bool(indeg and max(indeg.values()) >= 3)

        def _denom():
            return len(clean_edges) + unresolved

        if depth >= DEPTH_CUTOFF:
            chains = longest_callable_chains(g)
            _stars = a.get("stars_gh") or 0
            _created = (a.get("created_at") or "")[:10]
            rows.append(
                {
                    "repo": name,
                    "depth": depth,
                    "nodes_clean": raw_n - sum(1 for n in nodes if "/" in n["id"] or ":" in n["id"]),
                    "edges_clean": len(clean_edges),
                    "unresolved_depends": unresolved,
                    "unresolved_pct": round(100 * unresolved / max(_denom(), 1), 1),
                    "has_fanout_hub>=3": has_hub,
                    "is_fork": 1 if (a.get("fork", False) or a.get("archived", False)) else 0,
                    "stars_gh": _stars,
                    "created_at": _created,
                    "longest_clean_chain": len(chains[0]) if chains else 0,
                    "chain": " -> ".join(chains[0]) if chains else "",
                    "n_max_chains": len(chains),
                }
            )
            tail.append(rows[-1])
            unresolved_deep_share.append(rows[-1]["unresolved_pct"])
            nodes_clean_tail.append(rows[-1]["nodes_clean"])
            edges_clean_tail.append(rows[-1]["edges_clean"])
            depth_of_tail.append(depth)
            longest_chain_len.append(rows[-1]["longest_clean_chain"])
            fanout_hub_tail += 1 if has_hub else 0
            fork_or_archived_tail += rows[-1]["is_fork"]

    # ---- write CSV ----
    with open(OUT_DIR / "rq3_depth_tail.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "repo", "depth", "nodes_clean", "edges_clean", "unresolved_depends",
            "unresolved_pct", "has_fanout_hub>=3", "is_fork", "stars_gh",
            "created_at", "longest_clean_chain", "chain", "n_max_chains",
        ])
        w.writeheader()
        for r in sorted(rows, key=lambda r: (-r["depth"], r["repo"])):
            w.writerow(r)

    # ---- summary ----
    n_tail = len(tail)

    print(f"Accepted (with reports): {len(accepted)}")
    print(f"Graph-bearing repos:      {gb}")
    print(f"Depth histogram (graph-bearing): {dict(sorted(depth_hist.items()))}")
    print(f"Deep tail (depth >= {DEPTH_CUTOFF}): {n_tail} repos ({100 * n_tail / gb:.1f}% of graph-bearing; "
          f"{100 * n_tail / len(accepted):.1f}% of census)")
    print()
    if n_tail:
        print(f"  depth distribution in tail:   {dict(collections.Counter(depth_of_tail))}")
        print(f"  median (IQR) nodes_clean:      {st.median(nodes_clean_tail):.0f} "
              f"({iqr_q(nodes_clean_tail)})  [census median 19]")
        print(f"  median (IQR) edges_clean:      {st.median(edges_clean_tail):.0f} "
              f"({iqr_q(edges_clean_tail)})")
        print(f"  median unresolved %%:           {st.median(unresolved_deep_share):.1f}%")
        print(f"  with fan-out hub (>=3):        {fanout_hub_tail}/{n_tail} ({100 * fanout_hub_tail / n_tail:.1f}%)")
        print(f"  forks/archived in tail:        {fork_or_archived_tail}")
        print(f"  median longest clean chain:    {st.median(longest_chain_len)}")
        print()
        # walkable/fully-resolvable chains
        resolvable = [r for r in tail if r["unresolved_pct"] == 0.0]
        print(f"  tail repos at 0% unresolved:   {len(resolvable)}/{n_tail}")
        print(f"  tail repos with fully pulled chains: {sum(1 for r in resolvable if r['longest_clean_chain'] == r['depth'])}")


def iqr_q(vals: list[int]) -> str:
    if len(vals) < 2:
        return "-"
    q1, _, q3 = st.quantiles([float(v) for v in vals], n=4)
    return f"{q1:.0f}-{q3:.0f}"


if __name__ == "__main__":
    main()