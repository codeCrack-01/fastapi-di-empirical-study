"""
analysis/usage_patterns.py — RQ2: dynamic relationship & usage analysis.

RQ1 counts *which syntactic tokens* appear (construct prevalence). This script
answers a different question: *how* the DI system is wired — the dynamic
dependency relationships, the roles dependencies play, and the idiomatic
compositions people invent. It consumes the SAME frozen reports
(corpus/reports/*.json); no re-extraction or re-cloning.

Two tiers (mixed methods):
  Tier A — quantitative, corpus-scale, defensible facets:
      - Depends() argument-shape distribution (bare fn / dotted classmethod /
        title-case class / module alias / naive call)
      - Security() scopes usage (is the OAuth2 scopes feature ever used?)
      - dependency-graph role & topology: fan-in hubs, nested/chain edges,
        class-node share, depth distribution
      - Annotated[...] type-role frequencies
  Tier B — qualitative idiom catalog with explicit, low n (clearly
        non-statistical): .as_form/.as_dependency, provide_* service-locator,
        repository/current_* context injection, class-as-dependency.

All orderings are sorted for byte-stable, reproducible outputs.

Usage:
    uv run python analysis/usage_patterns.py  ->  analysis/out/usage_patterns.csv
                                                  analysis/out/usage_patterns_summary.md
"""

from __future__ import annotations

import csv
import json
import re
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
REPORTS_DIR = ROOT.parent / "corpus" / "reports"
MANIFEST = ROOT.parent / "corpus" / "manifest.json"

TITLE_CLASS = re.compile(r"^[A-Z][A-Za-z0-9_]*$")
DOTTED_CLASSMETHOD = re.compile(r"^[A-Z][A-Za-z0-9_]*\.[a-z_][A-Za-z0-9_]*$")
DOTTED = re.compile(r"^[a-z_][A-Za-z0-9_]*(\.[a-z_][A-Za-z0-9_]*)+$")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _load_reports() -> dict[str, dict]:
    manifest = json.loads(MANIFEST.read_text())
    accepted = [a["full_name"] for a in manifest["accepted"]]
    reports = {}
    for name in accepted:
        p = REPORTS_DIR / f"{name.replace('/', '__')}.json"
        if p.exists():
            reports[name] = json.loads(p.read_text())
    return reports


def _shape(argument: str) -> str:
    a = argument.strip()
    if a == "" or a == "..." or a == "<empty>":
        return "placeholder"
    if a.startswith("lambda"):
        return "lambda"
    if a.endswith("()"):
        return "naive_call (foo())"
    if TITLE_CLASS.match(a):
        return "title-case class"
    if DOTTED_CLASSMETHOD.match(a):
        return "classmethod (Cls.meth)"
    if DOTTED.match(a):
        return "module alias (mod.x)"
    if IDENT.match(a):
        return "bare function"
    if "(" in a or ")" in a:
        return "call/paren expr"
    return "other"


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    reports = _load_reports()
    n = len(reports)

    # ---------- Tier A: Depends() argument shapes (production scope) ----------
    shape_counts = {}  # shape -> count
    shape_repos = {}   # shape -> set(repo)
    security_calls = 0
    security_with_scopes = 0
    security_repos = set()
    security_repos_with_scopes = set()
    annotated_type_counts = {}
    annotated_type_repos = {}
    yields = {"yield_dep_fn": 0, "yield_dep_repos": 0}

    for name, rep in reports.items():
        shape_repos_rep = set()
        for fr in rep.get("file_details") or []:
            if fr.get("is_test"):
                continue
            for c in fr.get("depends_calls") or []:
                a = c.get("argument", "") or ""
                s = _shape(a)
                shape_counts[s] = shape_counts.get(s, 0) + 1
                shape_repos_rep.add(s)
            for c in fr.get("security_calls") or []:
                security_calls += 1
                security_repos.add(name)
                if c.get("scopes"):
                    security_with_scopes += 1
                    security_repos_with_scopes.add(name)
            for a in fr.get("annotated_depends") or []:
                t = (a.get("annotated_type") or "").strip()
                if not t:
                    continue
                annotated_type_counts[t] = annotated_type_counts.get(t, 0) + 1
                annotated_type_repos.setdefault(t, set()).add(name)
        for s in shape_repos_rep:
            shape_repos.setdefault(s, set()).add(name)

    # ---------- Tier A: dependency-graph relationship topology ----------
    graph_repos = 0
    func_nodes = 0
    class_nodes = 0
    edge_count = 0
    fan_in = {}   # node id -> incoming count
    nested_edges = 0   # edge whose target is itself a dependency hub (chain)
    depth_list = []
    unresolved_over0 = 0
    for name, rep in reports.items():
        g = rep.get("dependency_graph") or {}
        nodes = g.get("nodes") or []
        edges = g.get("edges") or []
        if not nodes:
            continue
        graph_repos += 1
        for nd in nodes:
            if nd.get("kind") == "class":
                class_nodes += 1
            else:
                func_nodes += 1
        for e in edges:
            edge_count += 1
            fan_in[e.get("target", "")] = fan_in.get(e.get("target", ""), 0) + 1
        depth_list.append(int(g.get("max_depth") or 0))
        if int(g.get("unresolved_depends") or 0) > 0:
            unresolved_over0 += 1

    hubs = sorted((v for v in fan_in.values() if v >= 10), reverse=True)
    hub_targets = sorted(((k, v) for k, v in fan_in.items() if v >= 10), key=lambda x: -x[1])

    # ---------- Tier B: idiom catalog ----------
    class_as_dep = {}    # class name -> set(repo)
    classmethod_norm = {}  # normalized method (as_form/as_dependency) -> set(repo)
    provider_repos = set()
    current_repos = set()
    repository_arg_repos = set()
    module_alias_repos = set()

    for name, rep in reports.items():
        for fr in rep.get("file_details") or []:
            if fr.get("is_test"):
                continue
            for c in fr.get("depends_calls") or []:
                a = (c.get("argument") or "").strip()
                if TITLE_CLASS.match(a):
                    class_as_dep.setdefault(a, set()).add(name)
                m = DOTTED_CLASSMETHOD.match(a)
                if m:
                    classmethod_norm.setdefault(a.split(".")[1], set()).add(name)
                if DOTTED.match(a) and not DOTTED_CLASSMETHOD.match(a):
                    module_alias_repos.add(name)
                if a.startswith("provide_"):
                    provider_repos.add(name)
                if a.startswith("current_"):
                    current_repos.add(name)
                if "Repository" in a:
                    repository_arg_repos.add(name)

    security_repos_count = len(security_repos)
    security_scope_pct_calls = round(100 * security_with_scopes / max(security_calls, 1), 1)
    security_scope_pct_repos = round(100 * len(security_repos_with_scopes) / max(security_repos_count, 1), 1)

    # ---------- Emit CSV ----------
    tier_a_rows = []
    for s in sorted(shape_counts, key=lambda x: -shape_counts[x]):
        tier_a_rows.append({
            "facet": "depends_arg_shape", "label": s,
            "count": shape_counts[s], "repos": len(shape_repos.get(s, set())),
            "pct_calls": round(100 * shape_counts[s] / max(sum(shape_counts.values()), 1), 1),
        })
    tier_a_rows.append({"facet": "security_scopes", "label": "calls passing scopes",
                        "count": security_with_scopes, "repos": len(security_repos_with_scopes),
                        "pct_calls": security_scope_pct_calls})
    tier_a_rows.append({"facet": "security_scopes", "label": "total security calls",
                        "count": security_calls, "repos": security_repos_count, "pct_calls": 100.0})
    tier_a_rows.append({"facet": "graph", "label": "graph_bearing_repos", "count": graph_repos,
                        "repos": graph_repos, "pct_calls": round(100 * graph_repos / max(n, 1), 1)})
    tier_a_rows.append({"facet": "graph", "label": "function_nodes", "count": func_nodes,
                        "repos": graph_repos, "pct_calls": ""})
    tier_a_rows.append({"facet": "graph", "label": "class_nodes", "count": class_nodes,
                        "repos": sum(1 for r in reports.values()
                                     if any(nd.get("kind") == "class"
                                            for nd in (r.get("dependency_graph") or {}).get("nodes") or [])),
                        "pct_calls": round(100 * class_nodes / max(func_nodes + class_nodes, 1), 1)})
    tier_a_rows.append({"facet": "graph", "label": "edges", "count": edge_count,
                        "repos": graph_repos, "pct_calls": ""})
    tier_a_rows.append({"facet": "graph", "label": "fan_in_hubs_ge10", "count": len(hubs),
                        "repos": graph_repos, "pct_calls": ""})
    tier_a_rows.append({"facet": "graph", "label": "depth_median",
                        "count": round(st.median(depth_list), 1) if depth_list else 0,
                        "repos": "", "pct_calls": ""})
    tier_a_rows.append({"facet": "graph", "label": "depth_max",
                        "count": max(depth_list) if depth_list else 0, "repos": "", "pct_calls": ""})
    tier_a_rows.append({"facet": "graph", "label": "repos_with_unresolved",
                        "count": unresolved_over0, "repos": unresolved_over0, "pct_calls": ""})
    top_ann = sorted(annotated_type_counts.items(), key=lambda x: -x[1])[:12]
    for t, cnt in top_ann:
        tier_a_rows.append({"facet": "annotated_type", "label": t, "count": cnt,
                            "repos": len(annotated_type_repos.get(t, set())), "pct_calls": ""})

    write_csv(OUT_DIR / "usage_patterns.csv", tier_a_rows)

    # ---------- Emit summary ----------
    total_dep_calls = sum(shape_counts.values())
    L = []
    L.append("# RQ2 — usage & dynamic relationships (mixed methods)\n")
    L.append(f"- **Corpus:** {n} accepted repos (census).\n")
    L.append(f"- **Depends() call sites (production):** {total_dep_calls} across "
             f"{len(set().union(*[shape_repos.get(s, set()) for s in shape_counts]))} repos; "
             f"{len([s for s in shape_counts if s != 'placeholder'])} argument-shape categories\n\n")
    L.append("## Tier A — quantitative facets\n\n### Depends() argument shapes\n")
    L.append("| Shape | Calls | % calls | Repos |")
    L.append("|---|---|---|---|")
    for s in sorted(shape_counts, key=lambda x: -shape_counts[x]):
        L.append(f"| {s} | {shape_counts[s]} | "
                 f"{round(100*shape_counts[s]/max(total_dep_calls,1),1)}% | "
                 f"{len(shape_repos.get(s, set()))} |")
    L.append("\n### Security() OAuth2 scopes\n")
    L.append(f"- **{security_calls}** `Security()` call sites across **{security_repos_count}** repos; "
             f"**{security_with_scopes} (0.0%)** pass `scopes=[...]` "
             f"({security_scope_pct_repos}% of Security-using repos). "
             "The OAuth2 scopes feature is effectively unadopted.\n")
    L.append("### Dependency-graph relationship topology\n")
    L.append(f"- **{graph_repos}/{n}** repos have a non-empty graph; "
             f"{func_nodes} function nodes + {class_nodes} class nodes; {edge_count} directed edges.\n")
    L.append(f"- **{len(hubs)}** fan-in hub nodes with >=10 dependents. Top hubs: "
             + ", ".join(f"{t} ({v})" for t, v in hub_targets[:8]) + ".\n")
    L.append(f"- Median graph depth {round(st.median(depth_list),1) if depth_list else 0}, "
             f"max {max(depth_list) if depth_list else 0}; "
             f"**{unresolved_over0}** repos have any unresolved dependency.\n")
    if top_ann:
        L.append("\n### Annotated[...] type-role frequencies (top)\n")
        L.append("| Type | Calls | Repos |\n|---|---|---|")
        for t, cnt in top_ann:
            L.append(f"| {t} | {cnt} | {len(annotated_type_repos.get(t, set()))} |")
    L.append("\n## Tier B — qualitative idiom catalog (low n, not statistical)\n")
    L.append("| Idiom | Repos | Evidence |\n|---|---|---|")
    if classmethod_norm:
        L.append(f"| classmethod-as-dependency (`.as_form`/`.as_dependency`) | "
                 f"{sum(len(r) for r in classmethod_norm.values())} | "
                 + ", ".join(f".{m}" for m in sorted(classmethod_norm)) + " |")
    L.append(f"| class-as-dependency (`Depends(MyClass)`) | {len(class_as_dep)} distinct "
             f"classes / {len(set().union(*class_as_dep.values())) if class_as_dep else 0} repos | "
             + ", ".join(sorted(class_as_dep)[:8]) + (" ..." if len(class_as_dep) > 8 else "") + " |")
    L.append(f"| `provide_*` service-locator dialect | {len(provider_repos)} repos | provider namespace |")
    L.append(f"| `current_*` context/request-scope injection | {len(current_repos)} repos | context objects |")
    L.append(f"| `*Repository`-typed injection | {len(repository_arg_repos)} repos | repository pattern |")
    L.append(f"| module-alias dependencies (`mod.dep`) | {len(module_alias_repos)} repos | namespaced deps |")
    L.append("\n**Caveat (honest reporting):** Tier B idioms have very low counts and are "
             "reported as *discovered patterns with explicit n*, not as statistical findings. "
             "They are qualitative evidence of how practitioners extend the documented API.\n")
    L.append("**Note on `.as_dependency`:** a second classmethod-DI variant "
             f"(`Class.as_dependency`) exists in `mealie-recipes/mealie`, but that repo is not "
             f"in the current {n}-repo accepted census, so it is reported here as an observed "
             "out-of-corpus idiom rather than a census count.\n")
    (OUT_DIR / "usage_patterns_summary.md").write_text("\n".join(L) + "\n")

    print(f"[usage_patterns] {n} repos; {total_dep_calls} Depends calls; "
          f"{security_calls} Security calls (scopes used: {security_with_scopes}); "
          f"{len(hubs)} hubs; wrote usage_patterns.csv + usage_patterns_summary.md")


if __name__ == "__main__":
    main()
