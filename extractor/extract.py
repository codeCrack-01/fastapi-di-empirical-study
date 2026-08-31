from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime

import ast

from config import (
    EXTRACTOR_VERSION,
    FILE_PATTERNS,
    IGNORED_DIRS,
    IGNORED_FILES,
    SCHEMA_VERSION,
    TEST_INDICATORS,
    is_test_file,
)
from models import (
    FileReport,
    RepoAggregate,
    RepoCoverage,
    RepoMetadata,
    RepoReport,
)
from resolver import CrossFileResolver
from visitor import FastAPIVisitor


def should_ignore(entry: pathlib.Path) -> bool:
    if entry.name.startswith("."):
        return True
    if entry.name in IGNORED_DIRS:
        return True
    if entry.name in IGNORED_FILES:
        return True
    if entry.is_dir() and entry.name in {d.strip("/") for d in TEST_INDICATORS if d.endswith("/")}:
        return False
    return False


def get_git_sha(repo_path: pathlib.Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return ""


def analyze_file(file_path: pathlib.Path) -> Optional[FileReport]:
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    visitor = FastAPIVisitor(file_path)
    visitor.visit(tree)
    visitor.post_process()
    report = visitor.report
    report.imports_fastapi = visitor._fastapi_imported
    report.is_test = is_test_file(file_path)
    report.non_fastapi_depends_sources = visitor.non_fastapi_depends_sources
    return report


def analyze_repo(repo_path: pathlib.Path) -> RepoReport:
    repo_path = repo_path.resolve()
    repo_name = repo_path.name
    sha = get_git_sha(repo_path)
    file_reports: list[FileReport] = []
    all_py_files = sorted(
        repo_path.rglob("*.py"),
        key=lambda p: p.relative_to(repo_path).as_posix(),
    )
    for py_file in all_py_files:
        rel = py_file.relative_to(repo_path)
        parts = rel.parts
        if any(part.startswith(".") for part in parts):
            continue
        if any(part in IGNORED_DIRS for part in parts):
            continue
        if py_file.name in IGNORED_FILES:
            continue
        fr = analyze_file(py_file)
        if fr is not None:
            file_reports.append(fr)
    production_reports = [fr for fr in file_reports if not fr.is_test]
    test_reports = [fr for fr in file_reports if fr.is_test]
    coverage = RepoCoverage(
        files_total=len(file_reports),
        files_production=len(production_reports),
        files_test=len(test_reports),
        pct_production=round(len(production_reports) / max(len(file_reports), 1), 4),
    )
    report = RepoReport(
        schema_version=SCHEMA_VERSION,
        extractor_version=EXTRACTOR_VERSION,
        repo=RepoMetadata(
            name=repo_name,
            commit_sha=sha,
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
        ),
        coverage=coverage,
        aggregate=RepoAggregate(),
        file_details=file_reports,
    )
    resolver = CrossFileResolver(repo_path, production_reports)
    resolver.build_dependency_graph(report, production_reports)
    yield_usage = resolver.compute_yield_usage(production_reports)
    used_yield_names: set[str] = set()
    for yf in yield_usage:
        if yf.used_as_dependency:
            used_yield_names.add(yf.name)
            for fr in report.file_details:
                for yf2 in fr.yield_functions:
                    if yf2.name == yf.name and yf2.line == yf.line:
                        yf2.used_as_dependency = True
    class_dep_results = resolver.collect_callable_class_deps(production_reports)
    non_fastapi_depends: dict[str, set[str]] = {}
    for fr in production_reports:
        for asname, module in fr.non_fastapi_depends_sources.items():
            if module not in non_fastapi_depends:
                non_fastapi_depends[module] = set()
            non_fastapi_depends[module].add(asname)
    aggregate = _compute_aggregate(production_reports, used_yield_names)
    report.aggregate = aggregate
    if test_reports:
        report.test_aggregate = _compute_aggregate(test_reports, set())
    observations: list[str] = []
    if report.aggregate.annotated_depends_total == 0 and report.aggregate.depends_total > 10:
        observations.append(
            "Uses traditional Depends() pattern extensively but no Annotated[..., Depends(...)]"
        )
    if report.aggregate.override_total == 0 and report.test_aggregate and report.test_aggregate.override_total > 0:
        observations.append(
            "dependency_overrides found only in test code, not in production"
        )
    if report.aggregate.yield_dep_total == 0 and report.aggregate.depends_total > 10:
        observations.append(
            "No yield-based generator dependencies despite significant Depends usage"
        )
    if non_fastapi_depends:
        for source, names in non_fastapi_depends.items():
            observations.append(
                f"Depends imported from non-fastapi source '{source}': {', '.join(sorted(names))}"
            )
    if class_dep_results:
        observations.append(
            f"Cross-file callable class deps: {', '.join(c[0] for c in class_dep_results[:5])}"
        )
    report.observations = observations
    return report


def _compute_aggregate(
    reports: list[FileReport],
    used_yield_names: set[str] | None = None,
) -> RepoAggregate:
    agg = RepoAggregate()
    fastapi_files = 0
    used_yield_names = used_yield_names or set()
    for fr in reports:
        if fr.imports_fastapi:
            fastapi_files += 1
        agg.fastapi_app_count += fr.fastapi_app_count
        agg.depends_total += len(fr.depends_calls)
        agg.security_total += len(fr.security_calls)
        agg.annotated_depends_total += len(fr.annotated_depends)
        agg.yield_dep_total += sum(
            1 for yf in fr.yield_functions if yf.used_as_dependency or yf.name in used_yield_names
        )
        agg.router_dep_total += len(fr.router_dep_calls)
        agg.app_dep_total += len(fr.app_dep_calls)
        agg.override_total += len(fr.override_calls)
        agg.callable_class_dep_total += len(fr.callable_class_deps)
    agg.files_importing_fastapi = fastapi_files
    return agg


def main():
    parser = argparse.ArgumentParser(description="Extract FastAPI DI usage from a repository")
    parser.add_argument("repo_path", type=str, help="Path to the repository to analyze")
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output path for JSON report (default: stdout)"
    )
    parser.add_argument(
        "--pretty", "-p", action="store_true", default=True,
        help="Pretty-print JSON output"
    )
    args = parser.parse_args()
    repo_path = pathlib.Path(args.repo_path)
    if not repo_path.exists() or not repo_path.is_dir():
        print(f"Error: {repo_path} is not a valid directory", file=sys.stderr)
        sys.exit(1)
    report = analyze_repo(repo_path)
    json_str = report.model_dump_json(indent=2 if args.pretty else None)
    if args.output:
        out_path = pathlib.Path(args.output)
        out_path.write_text(json_str)
        print(f"Report written to {out_path}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
