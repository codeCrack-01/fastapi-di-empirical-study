"""config_hash.py — sha256 over the exact files that define the study config.

A pre-registration is only useful if the thing it describes is pinned. This
hash covers the files that determine what is measured:

  generator   how the 8 apps are built, from one route table
  service     the SQL and response payloads
  routes      the 12 read routes
  pool        connection acquisition, held constant across both models
  runner      worker count, core pinning, warmup/window/cooldown, the cell loop
  knee        how the knee is located and which rates qualify
  harness     the k6 workload mix and window bucketing
  database    the read-only seed builder and its verification
  smoke       the functional-equivalence gate
  analysis    the statistics

Any edit to any of these invalidates the pre-registration and requires a new
hash and an explicit amendment. Run before the study, commit the value.

Run:  python config_hash.py
"""

from __future__ import annotations

import hashlib
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
    ("knee", "knee.py"),
    ("harness", "k6/harness.js"),
    ("database", "build_db.py"),
    ("smoke", "smoke.py"),
    ("analysis", "analyze.py"),
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
    out = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    for mod in ("fastapi", "starlette", "anyio", "pydantic", "uvicorn",
                "aiosqlite", "dependency_injector"):
        try:
            m = __import__(mod)
            out[mod] = getattr(m, "__version__", "unknown")
        except ImportError:
            out[mod] = "not installed"
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
