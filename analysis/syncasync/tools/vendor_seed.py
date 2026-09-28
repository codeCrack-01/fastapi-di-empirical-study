#!/usr/bin/env python3
"""Regenerate _seed_source.py from the archived experiment tree.

The study box receives only analysis/syncasync, so it cannot import
analysis/experiment/core/db.py. This vendors the schema and seed rows as a
literal, and the output is verified by build_db.py reproducing the database
sha256 recorded in docs/prereg_execution_model.md.

Run only when the archived seed changes; the hash check will catch it if the
regenerated file does not reproduce the recorded database.

    python tools/vendor_seed.py
"""

import json
import pathlib
import sqlite3
import sys

HERE = pathlib.Path(__file__).resolve().parent
SYNCASYNC = HERE.parent
sys.path.insert(0, str(SYNCASYNC.parent / "experiment"))

from core.db import _SCHEMA, _seed  # noqa: E402


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    _seed(conn)
    conn.commit()
    tables = [r[0] for r in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    rows = {t: [dict(r) for r in conn.execute(f'SELECT * FROM "{t}"')] for t in tables}

    body = (
        '"""Vendored schema and seed data for the read-only benchmark database.\n\n'
        "Generated from analysis/experiment/core/db.py so the study box (which receives\n"
        "only analysis/syncasync) can rebuild the database byte-identically without the\n"
        "archived experiment tree. Do not hand-edit: regenerate with\n"
        "tools/vendor_seed.py.\n"
        '"""\n\n'
        "SCHEMA = " + json.dumps(_SCHEMA, indent=4) + "\n\n"
        "SEED_ROWS = " + json.dumps(rows, indent=4) + "\n"
    )
    out = SYNCASYNC / "_seed_source.py"
    out.write_text(body)
    print(f"wrote {out} ({len(body)} bytes)")
    print(f"  tables: { {k: len(v) for k, v in rows.items()} }")


if __name__ == "__main__":
    main()
