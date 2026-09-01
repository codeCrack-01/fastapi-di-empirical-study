"""
analysis/e6_structural.py — offline structural-sophistication signals for E6.

Reads the local depth-1 clones only (no network). For every accepted repo it
emits a vector of binary structural signals (packaging, ops/deploy, schema/db,
auth, caching, integrations, tests) plus clone-scale metrics (py files, LOC,
package count) and a composite sophistication index — the sum of the binary
signals. The output joins each row to manifest metadata (tutorial flag,
markers, stars).

This powers the E6 pattern analysis: whether structural sophistication
separates flagged (tutorial-marker) repos from the unflagged baseline, and
whether demo-labeled repos lack the db/auth/cache/integration signals that
genuine apps carry. It is a descriptive pattern probe, not a classifier.

Usage:
    uv run python analysis/e6_structural.py
Output:
    analysis/out/e6_structural.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"

IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "dist", "build", ".tox", ".egg-info", "htmlcov", ".mypy_cache",
    ".pytest_cache", "site-packages", ".idea", ".vscode", ".github",
}

MARKER_FILES = {
    "Dockerfile": {"Dockerfile", "Dockerfile.*", "*.dockerfile"},
    "docker-compose": {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"},
    "helm": {"Chart.yaml"},
}

# Package names (lowercase) that indicate a non-trivial integration, worker,
# auth, or caching substrate when declared as a dependency or imported.
INTEGRATION_DEPS = {
    "boto3", "botocore", "openai", "anthropic", "groq", "cohere",
    "langchain", "langgraph", "llama_index", "pinecone", "chromadb",
    "weaviate", "qdrant", "elasticsearch", "redis", "sqlalchemy",
    "psycopg2", "psycopg2-binary", "asyncpg", "motor", "pymongo",
    "clickhouse-driver", "snowflake-connector-python", "trino", "dask",
    "celery", "arq", "rq", "dramatiq", "faststream", "stripe", "twilio",
    "slack_sdk", "telegram", "google-cloud-*", "azure-*", "kubernetes",
    "docker", "prometheus_client", "sentry-sdk", "datadog", "httpx",
    "aiohttp", "requests", "numpy", "pandas", "scikit-learn",
}
WORKER_DEPS = {"celery", "arq", "rq", "dramatiq", "faststream", "taskiq", "huey", "scheduler"}
AUTH_DEPS = {"python-jose", "pyjwt", "passlib", "bcrypt", "python-multipart", "itsdangerous"}
CACHE_DEPS = {"redis", "cachetools"}

EXTERNAL_SDK_FILES = {
    "boto3", "openai", "anthropic", "groq", "cohere", "stripe", "twilio",
    "slack_sdk", "google.cloud", "azure.*", "kubernetes", "celery", "arq",
    "redis", "pinecone", "chromadb", "qdrant", "elasticsearch",
}
AUTH_IMPORTS = {"jose", "jwt", "passlib", "bcrypt"}
CACHE_IMPORTS = {"cachetools", "diskcache", "redis"}
ORM_IMPORTS = {"sqlalchemy", "peewee", "tortoise", "django.db", "motor.motor", "pymongo"}
WORKER_IMPORTS = {"celery", "arq", "rq", "dramatiq", "faststream", "taskiq", "huey"}


def _declared_deps(repo: Path) -> set[str]:
    """Collect lowercase declared dependency names from common manifest files."""
    deps: set[str] = set()
    for rel in ("pyproject.toml", "requirements.txt"):
        f = repo / rel
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")[:400_000]
        except OSError:
            continue
        if rel == "pyproject.toml":
            # [project] dependencies = [...]  and  [tool.poetry.dependencies]
            for m in re.finditer(r"([A-Za-z0-9_.\-]+)\s*(?:\[[^\]]*\])?\s*=", text):
                name = m.group(1).lower().strip()
                if name not in {"python"}:
                    deps.add(name)
        else:
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith(("#", "-", "[", "http", "git+")):
                    continue
                name = re.split(r"[=<>!~\[;]", line, maxsplit=1)[0].strip().lower()
                if name:
                    deps.add(name)
    return deps


def _import_split(name: str) -> str:
    # normalize module import: "google.cloud.foo" -> "google.cloud", "azure.storage" -> "azure.*"
    parts = name.split(".")
    if parts[0] in {"google", "azure"}:
        return parts[0] + "." + (parts[1] if len(parts) > 1 else "")
    return parts[0] if parts else ""


def _scan_unixfiles(repo: Path) -> tuple[set[str], set[str], dict]:
    """Return (imports, symbols, file-population metrics) across .py files."""
    imports: set[str] = set()
    symbols: set[str] = set()
    py_files = 0
    py_loc = 0
    packages: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        dp = Path(dirpath)
        rel = dp.relative_to(repo)
        if any(p in IGNORED_DIRS for p in rel.parts):
            continue
        has_init = "__init__.py" in filenames
        if has_init and rel != Path("."):
            packages.add(str(rel).replace(os.sep, "/"))
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            py_files += 1
            fp = dp / fn
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")[:800_000]
            except OSError:
                continue
            py_loc += text.count("\n")
            for m in re.finditer(r"^\s*(?:import|from)\s+([A-Za-z0-9_.]+)", text, re.M):
                mod = m.group(1)
                imports.add(_import_split(mod))
                imports.add(mod.split(".")[0])
            for sym in ("OAuth2PasswordBearer", "get_current_user", "lru_cache", "cached"):
                if f"\n{sym}" in text or f" {sym}" in text:
                    symbols.add(sym)
    return imports, symbols, {"py_files": py_files, "py_loc": py_loc, "packages": len(packages)}


def _has_any_file(repo: Path, names: set[str]) -> bool:
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        dp = Path(dirpath)
        rel = dp.relative_to(repo)
        if any(p in IGNORED_DIRS for p in rel.parts):
            continue
        for fn in filenames:
            if fn in names or any(fn.startswith(pat.rstrip("*").rstrip(".")) for pat in names if "*" in pat):
                return True
    return False


def _has_ci_workflow(repo: Path) -> bool:
    gw = repo / ".github" / "workflows"
    return gw.is_dir() and any(gw.iterdir())


def signal_profile(repo: Path) -> dict:
    deps = _declared_deps(repo)
    imports, symbols, pop = _scan_unixfiles(repo)

    # packaging / entry points
    pyproject = repo / "pyproject.toml"
    has_scripts = False
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8", errors="replace")[:400_000]
        has_scripts = bool(re.search(r"\[project\.scripts\]|\[tool\.poetry\.scripts\]", text))
    has_setup_py = (repo / "setup.py").exists() or (repo / "setup.cfg").exists()

    # ops / deploy
    has_dockerfile = _has_any_file(repo, MARKER_FILES["Dockerfile"])
    has_compose = _has_any_file(repo, MARKER_FILES["docker-compose"])
    has_ci = _has_ci_workflow(repo)
    has_makefile = (repo / "Makefile").exists()
    has_helm = _has_any_file(repo, {"Chart.yaml"})

    # schema / db
    has_migrations = (repo / "alembic").is_dir() or (repo / "migrations").is_dir()
    uses_orm = any(i in ORM_IMPORTS for i in imports) or "sqlalchemy" in deps
    has_sql_schema = _has_any_file(repo, {"init.sql", "schema.sql", "schema.graphql"})

    # auth / cache / workers / integrations
    uses_custom_auth = bool(imports & AUTH_IMPORTS) or bool(deps & AUTH_DEPS) or bool(symbols & {"OAuth2PasswordBearer", "get_current_user"})
    uses_cache = bool(imports & CACHE_IMPORTS) or bool(deps & CACHE_DEPS) or bool(symbols & {"lru_cache", "cached"})
    uses_workers = bool(imports & WORKER_IMPORTS) or bool(deps & WORKER_DEPS)
    integ_pkgs = sorted(deps & INTEGRATION_DEPS)

    # tests
    has_tests = (repo / "tests").is_dir() or (repo / "test").is_dir() or _has_any_file(repo, {"test_*.py", "*_test.py"})
    has_precommit = (repo / ".pre-commit-config.yaml").exists()

    profile = {
        "has_scripts": has_scripts,
        "has_setup_py": has_setup_py,
        "has_dockerfile": has_dockerfile,
        "has_compose": has_compose,
        "has_ci": has_ci,
        "has_makefile": has_makefile,
        "has_helm": has_helm,
        "has_migrations": has_migrations,
        "uses_orm": uses_orm,
        "has_sql_schema": has_sql_schema,
        "uses_custom_auth": uses_custom_auth,
        "uses_cache": uses_cache,
        "uses_workers": uses_workers,
        "has_tests": has_tests,
        "has_precommit": has_precommit,
        "integration_count": len(integ_pkgs),
        "py_files": pop["py_files"],
        "py_loc": pop["py_loc"],
        "packages": pop["packages"],
    }
    binary = [
        "has_scripts", "has_setup_py", "has_dockerfile", "has_compose", "has_ci",
        "has_makefile", "has_helm", "has_migrations", "uses_orm", "has_sql_schema",
        "uses_custom_auth", "uses_cache", "uses_workers", "has_tests", "has_precommit",
    ]
    profile["sophistication_index"] = sum(1 for k in binary if profile[k])
    return profile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT.parent / "corpus" / "manifest.json"))
    ap.add_argument("--clones", default=str(ROOT.parent / "study_repos" / "corpus"))
    ap.add_argument("--out", default=str(OUT_DIR / "e6_structural.csv"))
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    clones = Path(args.clones)
    rows = []
    for repo in sorted(manifest["accepted"], key=lambda r: r["full_name"]):
        full = repo["full_name"]
        clone = clones / full.replace("/", "__")
        markers = repo.get("tutorial_markers", "")
        marker_count = len(re.findall(r"'", markers)) if markers else 0
        row = {
            "repo": full,
            "tutorial_flag": bool(repo.get("tutorial_flag")),
            "marker_count": marker_count,
            "markers": markers,
            "stars_gh": repo.get("stars_gh"),
            "py_ratio": repo.get("py_ratio"),
        }
        if clone.is_dir():
            row.update(signal_profile(clone))
        else:
            row.update({k: False for k in ("has_scripts", "has_setup_py", "has_dockerfile",
                "has_compose", "has_ci", "has_makefile", "has_helm", "has_migrations",
                "uses_orm", "has_sql_schema", "uses_custom_auth", "uses_cache", "uses_workers",
                "has_tests", "has_precommit")})
            row["integration_count"] = 0
            row["py_files"] = row["py_loc"] = row["packages"] = 0
            row["sophistication_index"] = 0
        rows.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[e6_structural] {len(rows)} repos scanned -> {args.out}")


if __name__ == "__main__":
    main()