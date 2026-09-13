"""ReviewGate — in-process SQLite data layer (single source of truth).

Every strategy opens sessions/connections exactly through this module, so the
database conditions are constant by construction. Connections are per-request
(file-backed so the startup seed persists across connections).
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(
    os.environ.get("REVIEWGATE_DB", str(Path(__file__).resolve().parent.parent / "results" / "reviewgate.db"))
)


def make_connection(path=None) -> sqlite3.Connection:
    p = str(path or DB_PATH)
    conn = sqlite3.connect(p, check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


@contextmanager
def session(path=None):
    """Per-request session context (S0/S2/S3 acquisition primitive)."""
    conn = make_connection(path)
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """FastAPI-style generator dependency for the S1 spine."""
    with session() as conn:
        yield conn


_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL,               -- admin | editor | user
    auth_token TEXT UNIQUE NOT NULL,
    suspended INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author TEXT NOT NULL,
    status TEXT NOT NULL,             -- pending | approved | flagged | deleted
    rating INTEGER NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    review_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _init_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def _seed(conn: sqlite3.Connection) -> None:
    n = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if n:
        return
    conn.executemany(
        "INSERT OR IGNORE INTO users (id, username, email, role, auth_token) VALUES (?,?,?,?,?)",
        [
            (1, "alice", "alice@example.com", "admin", "admin-token"),
            (2, "bob", "bob@example.com", "admin", "bob-token"),
            (3, "carol", "carol@example.com", "admin", "carol-token"),
            (4, "dave", "dave@example.com", "editor", "editor-token"),
            (5, "erin", "erin@example.com", "editor", "erin-token"),
            (6, "frank", "frank@example.com", "user", "user-token"),
            (7, "grace", "grace@example.com", "user", "grace-token"),
            (8, "heidi", "heidi@example.com", "user", "heidi-token"),
            (9, "ivan", "ivan@example.com", "user", "ivan-token"),
        ],
    )
    conn.executemany(
        "INSERT OR IGNORE INTO reviews (id, title, body, author, status, rating, votes) VALUES (?,?,?,?,?,?,?)",
        [(i, f"Review {i}", f"Body of review {i}", ("alice" if i % 3 == 0 else "frank"), ("approved" if i % 5 else "pending"), (i % 5) + 1, i % 7) for i in range(1, 41)],
    )
    conn.executemany(
        "INSERT OR IGNORE INTO comments (id, review_id, author, body) VALUES (?,?,?,?)",
        [(i, (i % 40) + 1, "grace", f"Comment {i}") for i in range(1, 61)],
    )
    conn.executemany(
        "INSERT OR IGNORE INTO config (key, value) VALUES (?,?)",
        [("max_editors", "8"), ("backup_interval_h", "24"), ("audit_enabled", "true")],
    )
    conn.commit()


def init_database(path=None):
    """Create schema + seed once. Returns the resolved path. Idempotent."""
    p = Path(path or DB_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    with make_connection(p) as conn:
        _init_tables(conn)
        _seed(conn)
    return p