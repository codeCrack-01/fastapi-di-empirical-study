"""ReviewGate-R — read-only data layer, business logic, and connection pools.

One file defines the 12 read endpoints' logic. Two execution dialects render
from it:

    sync  : sqlite3 connection, `def` handlers, coroutines driven by resolve()
    async : aiosqlite connection, `async def` handlers, coroutines awaited

The service functions are `async def` even in the sync arm. That is deliberate:
it guarantees the SQL and the response payloads are *literally the same code*
in all 8 apps, so no arm can drift from another. In the sync arm the coroutine
never actually suspends, because a sqlite3 cursor is not awaitable, and
`resolve()` drives it to completion inline. The residual cost (one coroutine
frame per request) is measured in smoke and recorded in the pre-registration
as a known, quantified, uniform offset. It is identical across all 4 sync
patterns, so pattern-to-pattern comparison within the sync arm is unaffected.

Read paths only. The 9 write endpoints of the original app are deliberately
absent; the database is opened read-only. See docs/prereg_execution_model.md.

Connection policy is HELD CONSTANT across both execution models: a bounded
pool of POOL connections, each request leasing one exclusively for its
duration. This matters. Per-request aiosqlite connections would mean one OS
thread per request, and since the read-only workload has a knee in the
thousands of rps, thread creation churn would dominate and the async arm
would be measuring thread churn rather than the execution model. A pool of
equal size in both arms holds acquisition policy fixed so the only remaining
difference is sync-vs-async execution.
"""

from __future__ import annotations

import os
import queue
import sqlite3
import threading
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import HTTPException

DB_PATH = Path(
    os.environ.get(
        "REVIEWGATE_DB", str(Path(__file__).resolve().parent / "results" / "reviewgate_ro.db")
    )
)
POOL = int(os.environ.get("REVIEWGATE_POOL", "8"))

ROLES = {
    "public": [],
    "user": ["user", "editor", "admin"],
    "editor": ["editor", "admin"],
    "admin": ["admin"],
}


# --------------------------------------------------------------------------
# sync coroutine driver
# --------------------------------------------------------------------------

def resolve(coro):
    """Run a service coroutine to completion on the sync path.

    Raises if the coroutine ever truly suspends, which would mean a service
    reached a real awaitable on a sqlite3 cursor -- i.e. a bug in the shared
    service layer, not a legitimate outcome.
    """
    try:
        coro.send(None)
    except StopIteration as stop:
        return stop.value
    raise RuntimeError("sync arm: service coroutine suspended on a sync cursor")


# --------------------------------------------------------------------------
# cursors
# --------------------------------------------------------------------------

async def _cursor(conn, sql, params):
    """Normalise to a real cursor.

    sqlite3: conn.execute() returns a Cursor directly.
    aiosqlite: conn.execute() returns a `Result` that is awaitable; awaiting it
    yields the Cursor that actually has fetchone/fetchall.
    """
    out = conn.execute(sql, params)
    return await out if hasattr(out, "__await__") else out


async def _one(conn, sql, params=()):
    cur = await _cursor(conn, sql, params)
    row = cur.fetchone()
    return await row if hasattr(row, "__await__") else row


async def _all(conn, sql, params=()):
    cur = await _cursor(conn, sql, params)
    rows = cur.fetchall()
    return await rows if hasattr(rows, "__await__") else rows


# --------------------------------------------------------------------------
# connections (mode=ro everywhere: SQLite itself refuses writes)
# --------------------------------------------------------------------------

def make_sync_conn(path=None) -> sqlite3.Connection:
    conn = sqlite3.connect(
        f"file:{path or DB_PATH}?mode=ro",
        uri=True,
        check_same_thread=False,
        timeout=10.0,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


async def make_async_conn(path=None):
    import aiosqlite

    conn = await aiosqlite.connect(f"file:{path or DB_PATH}?mode=ro", uri=True, timeout=10.0)
    conn.row_factory = sqlite3.Row
    await conn.execute("PRAGMA busy_timeout=10000")
    return conn


# ---- sync pool: blocking checkout, so concurrent sync handlers queue ----

_sync_pool: "queue.Queue[sqlite3.Connection] | None" = None
_sync_lock = threading.Lock()


def _get_sync_pool(path=None):
    global _sync_pool
    with _sync_lock:
        if _sync_pool is None:
            q: queue.Queue = queue.Queue()
            for _ in range(POOL):
                q.put(make_sync_conn(path))
            _sync_pool = q
    return _sync_pool


@contextmanager
def sync_conn(path=None):
    q = _get_sync_pool(path)
    conn = q.get()
    try:
        yield conn
    finally:
        q.put(conn)


# ---- async pool: single event loop, so a plain free list needs no lock ----

_async_free: list = []


@asynccontextmanager
async def async_conn(path=None):
    conn = _async_free.pop() if _async_free else await make_async_conn(path)
    try:
        yield conn
    finally:
        _async_free.append(conn)


async def close_async_pool() -> None:
    """Close every pooled async connection.

    aiosqlite runs a non-daemon thread per connection, so without this the
    process hangs at exit instead of terminating. Call from the app lifespan
    teardown and at the end of any in-process test.
    """
    while _async_free:
        conn = _async_free.pop()
        try:
            await conn.close()
        except Exception:  # noqa: BLE001 -- teardown must not mask a test result
            pass


def close_sync_pool() -> None:
    global _sync_pool
    with _sync_lock:
        if _sync_pool is None:
            return
        while not _sync_pool.empty():
            try:
                _sync_pool.get_nowait().close()
            except Exception:  # noqa: BLE001
                pass
        _sync_pool = None


# --------------------------------------------------------------------------
# auth
# --------------------------------------------------------------------------

def bearer_token(headers) -> str | None:
    auth = headers.get("Authorization") or headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[len("Bearer "):].strip()


async def lookup_user(conn, token: str | None) -> dict | None:
    if not token:
        return None
    row = await _one(
        conn,
        "SELECT id, username, email, role, auth_token, suspended FROM users "
        "WHERE auth_token = ?",
        (token,),
    )
    return dict(row) if row else None


async def current_user(conn, request) -> dict:
    user = await lookup_user(conn, bearer_token(request.headers))
    if not user or user["suspended"]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_role(user: dict | None, roles: list) -> dict:
    if not user or user["role"] not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


# --------------------------------------------------------------------------
# business logic — the 12 read endpoints, written once
# --------------------------------------------------------------------------

async def health_check(conn) -> dict:
    await _one(conn, "SELECT 1")
    return {"ok": True}


async def list_reviews(conn, limit: int, offset: int) -> dict:
    rows = await _all(
        conn,
        "SELECT id, title, body, author, status, rating, votes FROM reviews "
        "WHERE status != 'deleted' ORDER BY id LIMIT ? OFFSET ?",
        (limit, offset),
    )
    total = await _one(conn, "SELECT COUNT(*) AS c FROM reviews WHERE status != 'deleted'")
    return {"items": [dict(r) for r in rows], "total": total["c"]}


async def get_review(conn, rid: int) -> dict:
    row = await _one(
        conn,
        "SELECT id, title, body, author, status, rating, votes FROM reviews WHERE id = ?",
        (rid,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return dict(row)


async def search_reviews(conn, q: str, limit: int) -> dict:
    like = f"%{q}%"
    rows = await _all(
        conn,
        "SELECT id, title, body, author, status, rating, votes FROM reviews "
        "WHERE status != 'deleted' AND (title LIKE ? OR body LIKE ?) ORDER BY id LIMIT ?",
        (like, like, limit),
    )
    return {"items": [dict(r) for r in rows], "total": len(rows)}


async def review_stats(conn) -> dict:
    rows = await _all(conn, "SELECT status, COUNT(*) AS c FROM reviews GROUP BY status")
    counts = {r["status"]: r["c"] for r in rows}
    return {
        "total": sum(counts.values()),
        "approved": counts.get("approved", 0),
        "flagged": counts.get("flagged", 0),
        "pending": counts.get("pending", 0),
    }


async def list_comments(conn, rid: int) -> dict:
    await get_review(conn, rid)
    rows = await _all(
        conn,
        "SELECT id, review_id, author, body FROM comments WHERE review_id = ? ORDER BY id",
        (rid,),
    )
    return {"items": [dict(r) for r in rows]}


async def me(conn, user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }


async def list_admins(conn) -> dict:
    rows = await _all(
        conn, "SELECT id, username, email, role FROM users WHERE role = 'admin' ORDER BY id"
    )
    return {"items": [dict(r) for r in rows]}


async def export_reviews(conn) -> dict:
    rows = await _all(
        conn, "SELECT id, title, body, author, status, rating, votes FROM reviews ORDER BY id"
    )
    return {"items": [dict(r) for r in rows], "total": len(rows)}


async def audit_trail(conn, uid: str) -> dict:
    rows = await _all(
        conn, "SELECT id, actor, action FROM audit WHERE actor = ? ORDER BY id", (uid,)
    )
    return {"items": [dict(r) for r in rows]}


async def admin_dashboard(conn) -> dict:
    n_users = await _one(conn, "SELECT COUNT(*) AS c FROM users")
    n_reviews = await _one(conn, "SELECT COUNT(*) AS c FROM reviews")
    n_approved = await _one(conn, "SELECT COUNT(*) AS c FROM reviews WHERE status = 'approved'")
    n_flags = await _one(conn, "SELECT COUNT(*) AS c FROM reviews WHERE status = 'flagged'")
    return {
        "n_users": n_users["c"],
        "n_reviews": n_reviews["c"],
        "n_approved": n_approved["c"],
        "n_flags": n_flags["c"],
    }


async def get_config(conn) -> dict:
    rows = await _all(conn, "SELECT key, value FROM config ORDER BY key")
    return {r["key"]: r["value"] for r in rows}
