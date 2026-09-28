"""config_hash.py — sha256 over the exact files that define the study config.

A pre-registration is only useful if the thing it describes is pinned. This
hash covers the files that determine what is measured:

  generator   how the 8 apps are built, from one route table
  service     the SQL and response payloads
  routes      the 12 read routes
  pool        connection acquisition, held constant across both models
  runner      worker count, core pinning, warmup/window/cooldown, the cell loop
  pinning     which siblings are offlined, and the disjointness check
  orchestrator the grid, the shuffle seed, the cell loop, per-arm rate selection
  knee        how the knee is located and which rates qualify
  smoke-knees single-probe knees for the smoke only; never a study knee
  harness     the k6 workload mix and window bucketing
  database    the read-only seed builder and its verification
  smoke       the functional-equivalence gate
  analysis    the statistics

Any edit to any of these invalidates the pre-registration and requires a new
hash and an explicit amendment. Run before the study, commit the value.

Note that run_matrix.py was added to this list in amendment 2: it selects each
arm's rate and defines the grid, so a pre-registration that omitted it was not
actually pinning what gets measured.

Run:  python config_hash.py
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (label, path relative to this file) -- the pre-registration quotes this list
CONFIG_FILES = [
    ("service", "core_read.py"),
    ("routes", "routes_read.py"),
    ("generator", "gen_apps.py"),
    ("pool+runner", "runner.py"),
    ("pinning", "prepare_box.py"),
    ("orchestrator", "run_matrix.py"),
    ("knee", "knee.py"),
    ("smoke-knees", "smoke_knees.py"),
    ("harness", "k6/harness.js"),
    ("database", "build_db.py"),
    ("seed", "_seed_source.py"),
    ("smoke", "smoke.py"),
    ("analysis", "analyze.py"),
    ("drift", "drift_report.py"),
]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def combined_hash() -> tuple[str, dict]:
    per_file = {}
    combined = hashlib.sha256()
    for label, rel in CONFIG_FILES:
        p = HERE / rel
        if not p.exists():
            raise SystemExit(f"FATAL: config file missing: {rel}")
        d = file_sha256(p)
        per_file[label] = {"file": rel, "sha256": d}
        # order matters and is fixed by CONFIG_FILES
        combined.update(f"{label}:{rel}:{d}\n".encode())
    return combined.hexdigest(), per_file


def versions() -> dict:
    """Exact runtime versions of everything the study's behaviour depends on.

    Uses importlib.metadata rather than __import__(m).__version__: anyio has no
    __version__ attribute, so the naive lookup reported "unknown" -- but the
    AnyIO threadpool size is a stated design parameter, so its version has to be
    recorded.
    """
    out = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    for dist, mod in (
        ("fastapi", "fastapi"), ("starlette", "starlette"), ("anyio", "anyio"),
        ("pydantic", "pydantic"), ("uvicorn", "uvicorn"),
        ("aiosqlite", "aiosqlite"), ("dependency-injector", "dependency_injector"),
    ):
        try:
            out[dist] = importlib.metadata.version(dist)
        except importlib.metadata.PackageNotFoundError:
            out[dist] = "not installed"
    try:
        import anyio
        # anyio.get_backend() only resolves inside a running event loop, so
        # sniff it there and fall back to uvicorn's default, which is asyncio.
        out["anyio_backend"] = anyio.get_backend()
    except Exception:  # noqa: BLE001
        out["anyio_backend"] = "asyncio (uvicorn default)"
    try:
        import subprocess
        out["k6"] = subprocess.run(["k6", "version"], capture_output=True,
                                   text=True).stdout.split()[1]
    except Exception:  # noqa: BLE001
        out["k6"] = "unknown"
    return out


def main() -> int:
    combined, per_file = combined_hash()
    payload = {
        "config_sha256": combined,
        "files": per_file,
        "versions": versions(),
        "database_sha256": file_sha256(HERE / "results" / "reviewgate_ro.db")
        if (HERE / "results" / "reviewgate_ro.db").exists() else None,
    }
    out = HERE / "results" / "config_hash.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))

    print(f"config_sha256  {combined}")
    print()
    for label, info in per_file.items():
        print(f"  {label:12s} {info['sha256'][:16]}  {info['file']}")
    print()
    for k, v in payload["versions"].items():
        print(f"  {k:20s} {v}")
    print()
    print(f"  database sha256  {(payload['database_sha256'] or 'n/a')[:16]}")
    print(f"written {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
