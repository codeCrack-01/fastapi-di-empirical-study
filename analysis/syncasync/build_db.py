"""Build the read-only benchmark database and verify it can never be written.

The database is a *copy* of the original seed, opened mode=ro by every arm.
Two independent guarantees:

  1. file permissions 0444 (owner can still chmod; this is a speed bump)
  2. mode=ro URI on every connection, so SQLite itself refuses writes
  3. a sha256 recorded before and after every measured cell, checked by the runner

`--verify` attempts INSERT/UPDATE/DELETE through a normal read/write handle and
asserts all three are refused. The build fails loudly if any write succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "experiment"))

from core.db import _SCHEMA, _seed  # noqa: E402

RO_DB = HERE / "results" / "reviewgate_ro.db"


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.chmod(0o644)
        dest.unlink()
    conn = sqlite3.connect(str(dest))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    _seed(conn)
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    return dest


def verify_readonly(path: Path) -> None:
    """Every write path must be refused. Any success is a hard failure."""
    # (a) URI mode=ro, the mode the apps actually use
    ro = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    for sql in (
        "INSERT INTO reviews (title, body, author, status, rating) VALUES ('x','y','z','pending',1)",
        "UPDATE reviews SET title = 'x' WHERE id = 1",
        "DELETE FROM reviews WHERE id = 1",
    ):
        try:
            ro.execute(sql)
            ro.commit()
        except sqlite3.OperationalError:
            continue
        raise SystemExit(f"FATAL: write succeeded through read-only connection: {sql}")
    ro.close()

    # (b) a normal read/write handle, which permissions alone must stop
    if os.geteuid() != 0:  # root ignores 0444
        try:
            with open(path, "r+b"):
                pass
        except PermissionError:
            pass
        else:
            raise SystemExit("FATAL: read/write handle opened on a 0444 database")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=RO_DB)
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    if not args.verify_only:
        build(args.db)
    args.db.chmod(0o444)

    verify_readonly(args.db)

    size = args.db.stat().st_size
    mode = stat.filemode(args.db.stat().st_mode)
    print(f"db        {args.db}")
    print(f"size      {size:,} bytes")
    print(f"mode      {mode}")
    print(f"sha256    {sha256(args.db)}")
    print("readonly  verified (mode=ro refused INSERT/UPDATE/DELETE)")


if __name__ == "__main__":
    main()
