from __future__ import annotations

import ast
import pathlib
from collections import defaultdict

from models import (
    DependsCall,
    DependencyGraph,
    FileReport,
    GraphEdge,
    GraphNode,
    RepoReport,
    YieldFunction,
)


class CrossFileResolver:
    def __init__(self, repo_path: pathlib.Path, file_reports: list[FileReport]):
        self.repo_path = repo_path
        self.file_reports = file_reports
        self._import_map: dict[str, dict[str, tuple[str, str]]] = {}
        self._function_defs: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self._class_defs: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self._module_path_cache: dict[str, pathlib.Path] = {}
        self._build_index()

    def _build_index(self):
        repo_root = self.repo_path.resolve()
        all_python = sorted(
            self.repo_path.rglob("*.py"),
            key=lambda p: p.relative_to(repo_root).as_posix(),
        )
        for py_file in all_python:
            rel = py_file.relative_to(repo_root).as_posix()
            module_path = rel.replace("/", ".").replace(".py", "")
            if module_path.endswith(".__init__"):
                module_path = module_path[:-9]
            elif module_path.endswith(".__init__"):
                module_path = module_path[:-9]
            self._module_path_cache[module_path] = py_file
            parts = rel.split("/")
            for i in range(1, len(parts)):
                sub = "/".join(parts[:i])
                sub_mod = sub.replace("/", ".")
                p = repo_root / sub / "__init__.py"
                if p.exists():
                    self._module_path_cache[sub_mod] = p
        for fr in self.file_reports:
            if not fr.imports_fastapi:
                continue
            p = fr.path
            rel = p.replace(".py", "")
            mod = rel.replace("/", ".")
            if mod.endswith(".__init__"):
                mod = mod[:-9]
            elif mod.endswith(".__init__"):
                mod = mod[:-9]
        for py_file in all_python:
            rel = py_file.relative_to(repo_root).as_posix()
            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._function_defs[node.name].append((rel, node.lineno))
                elif isinstance(node, ast.ClassDef):
                    self._class_defs[node.name].append((rel, node.lineno))

    def _module_for_file(self, file_path: str) -> str:
        if file_path.endswith(".py"):
            file_path = file_path[:-3]
        mod = file_path.replace("/", ".")
        if mod.endswith(".__init__"):
            mod = mod[:-9]
        return mod

    def resolve_depends_argument(self, arg_name: str, source_file: str) -> tuple[Optional[str], Optional[str]]:
        if arg_name == "<empty>" or arg_name == "...":
            return None, None
        found: Optional[str] = None
        found_line: Optional[str] = None
        if arg_name in self._function_defs:
            candidates = self._function_defs[arg_name]
            same_file = [c for c in candidates if c[0] == source_file]
            if same_file:
                found, found_line_num = same_file[0]
                found_line = f"{found}:{found_line_num}"
            else:
                found, found_line_num = candidates[0]
                found_line = f"{found}:{found_line_num}"
        if found is None and arg_name in self._class_defs:
            candidates = self._class_defs[arg_name]
            same_file = [c for c in candidates if c[0] == source_file]
            if same_file:
                found, found_line_num = same_file[0]
                found_line = f"{found}:{found_line_num}"
            else:
                found, found_line_num = candidates[0]
                found_line = f"{found}:{found_line_num}"
        return found, found_line

    def build_dependency_graph(self, report: RepoReport, production_reports: list[FileReport]):
        graph = DependencyGraph(scope="production")
        edges: list[tuple[str, str, str, str]] = []
        node_files: dict[str, str] = {}
        unresolved_count = 0
        for fr in production_reports:
            for dep in fr.depends_calls:
                source_name = dep.context_function or f"{fr.path}:{dep.line}"
                target_name = dep.argument
                if source_name and target_name and target_name not in ("<empty>", "..."):
                    resolved_file, resolved_line = self.resolve_depends_argument(target_name, fr.path)
                    if resolved_file:
                        edges.append((source_name, target_name, fr.path, resolved_file))
                        node_files[source_name] = fr.path
                        node_files[target_name] = resolved_file
                    else:
                        unresolved_count += 1
        seen_nodes: set[str] = set()
        for name, file_path in node_files.items():
            if name not in seen_nodes:
                graph.nodes.append(
                    GraphNode(
                        id=name,
                        file=file_path,
                        kind="function" if name in self._function_defs else "class",
                    )
                )
                seen_nodes.add(name)
        for src, tgt, src_f, tgt_f in edges:
            graph.edges.append(
                GraphEdge(source=src, target=tgt, source_file=src_f, target_file=tgt_f)
            )
        graph.max_depth = self._compute_max_depth(edges)
        graph.unresolved_depends = unresolved_count
        report.dependency_graph = graph

    def _compute_max_depth(self, edges: list[tuple[str, str, str, str]]) -> int:
        children: dict[str, list[str]] = defaultdict(list)
        parents: set[str] = set()
        children_set: set[str] = set()
        for src, tgt, _, _ in edges:
            children[src].append(tgt)
            children_set.add(tgt)
            parents.add(src)
        roots = parents - children_set
        if not roots:
            return 0 if not edges else 1
        max_d = 0
        for root in roots:
            depth = self._dfs_depth(root, children, set())
            if depth > max_d:
                max_d = depth
        return max_d

    def _dfs_depth(self, node: str, children: dict[str, list[str]], visited: set[str], depth: int = 1) -> int:
        if node in visited:
            return depth
        visited.add(node)
        if node not in children or not children[node]:
            return depth
        max_d = depth
        for child in children[node]:
            d = self._dfs_depth(child, children, visited.copy(), depth + 1)
            if d > max_d:
                max_d = d
        return max_d

    def compute_yield_usage(self, production_reports: list[FileReport]) -> list[YieldFunction]:
        all_dep_args: set[str] = set()
        for fr in production_reports:
            for dep in fr.depends_calls:
                if dep.argument not in ("<empty>", "..."):
                    all_dep_args.add(dep.argument)
        result: list[YieldFunction] = []
        for fr in production_reports:
            for yf in fr.yield_functions:
                yf.used_as_dependency = yf.name in all_dep_args
                result.append(yf)
        return result

    def collect_callable_class_deps(self, production_reports: list[FileReport]) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for fr in production_reports:
            for ccd in fr.callable_class_deps:
                resolved_file, resolved_line = self.resolve_depends_argument(ccd.class_name, fr.path)
                if resolved_file:
                    results.append((ccd.class_name, resolved_file))
                else:
                    results.append((ccd.class_name, fr.path))
        return results
