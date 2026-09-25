"""ReviewGate — business logic (single source of truth).

Handlers in every strategy call these exact functions. Connections are the
only dependency; authentication/role decisions are applied by the strategy's
acquisition layer BEFORE calling here (except where a guard is naturally part
of the operation, which then re-checks the passed user).
"""

from __future__ import annotations

import sqlite3

from fastapi import HTTPException


def _review(row) -> dict:
    return dict(row)


def health_check(conn) -> dict:
    conn.execute("SELECT 1").fetchone()
    return {"ok": True}


def list_reviews(conn, limit: int, offset: int) -> dict:
    rows = conn.execute(
        "SELECT id, title, body, author, status, rating, votes FROM reviews "
        "WHERE status != 'deleted' ORDER BY id LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) AS c FROM reviews WHERE status != 'deleted'").fetchone()["c"]
    return {"items": [_review(r) for r in rows], "total": total}


def get_review(conn, rid: int) -> dict:
    row = conn.execute(
        "SELECT id, title, body, author, status, rating, votes FROM reviews WHERE id = ?", (rid,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return _review(row)


def search_reviews(conn, q: str, limit: int) -> dict:
    like = f"%{q}%"
    rows = conn.execute(
        "SELECT id, title, body, author, status, rating, votes FROM reviews "
        "WHERE status != 'deleted' AND (title LIKE ? OR body LIKE ?) ORDER BY id LIMIT ?",
        (like, like, limit),
    ).fetchall()
    total = len(rows)
    return {"items": [_review(r) for r in rows], "total": total}


def review_stats(conn) -> dict:
    rows = conn.execute(
        "SELECT status, COUNT(*) AS c FROM reviews GROUP BY status"
    ).fetchall()
    counts = {r["status"]: r["c"] for r in rows}
    return {
        "total": sum(counts.values()),
        "approved": counts.get("approved", 0),
        "flagged": counts.get("flagged", 0),
        "pending": counts.get("pending", 0),
    }


def list_comments(conn, rid: int) -> dict:
    get_review(conn, rid)
    rows = conn.execute(
        "SELECT id, review_id, author, body FROM comments WHERE review_id = ? ORDER BY id", (rid,)
    ).fetchall()
    return {"items": [dict(r) for r in rows]}


def me(conn, user: dict) -> dict:
    return {"id": user["id"], "username": user["username"], "email": user["email"], "role": user["role"]}


def list_admins(conn) -> dict:
    rows = conn.execute(
        "SELECT id, username, email, role FROM users WHERE role = 'admin' ORDER BY id"
    ).fetchall()
    return {"items": [dict(r) for r in rows]}


def create_review(conn, title: str, body: str, rating: int, user: dict) -> dict:
    cur = conn.execute(
        "INSERT INTO reviews (title, body, author, status, rating, votes) VALUES (?,?,?,?,?,0)",
        (title, body, user["username"], "pending", rating),
    )
    conn.commit()
    return get_review(conn, cur.lastrowid)


def update_review(conn, rid: int, body, user: dict) -> dict:
    get_review(conn, rid)
    conn.execute(
        "UPDATE reviews SET title = ?, body = ?, rating = ? WHERE id = ?",
        (body.title, body.body, body.rating, rid),
    )
    conn.commit()
    return get_review(conn, rid)


def delete_review(conn, rid: int, user: dict) -> dict:
    get_review(conn, rid)
    conn.execute("UPDATE reviews SET status = 'deleted' WHERE id = ?", (rid,))
    conn.commit()
    return {"ok": True}


def flag_review(conn, rid: int, user: dict) -> dict:
    get_review(conn, rid)
    conn.execute("UPDATE reviews SET status = 'flagged' WHERE id = ?", (rid,))
    conn.commit()
    return get_review(conn, rid)


def vote(conn, rid: int, value: int, user: dict) -> dict:
    get_review(conn, rid)
    conn.execute("UPDATE reviews SET votes = votes + ? WHERE id = ?", (value, rid))
    conn.commit()
    return get_review(conn, rid)


def approve_review(conn, rid: int, user: dict) -> dict:
    get_review(conn, rid)
    conn.execute("UPDATE reviews SET status = 'approved' WHERE id = ?", (rid,))
    conn.commit()
    return get_review(conn, rid)


def export_reviews(conn) -> dict:
    rows = conn.execute(
        "SELECT id, title, body, author, status, rating, votes FROM reviews ORDER BY id"
    ).fetchall()
    return {"items": [_review(r) for r in rows], "total": len(rows)}


def suspend_user(conn, uid: str, user: dict) -> dict:
    row = conn.execute("SELECT id FROM users WHERE username = ?", (uid,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    conn.execute("UPDATE users SET suspended = 1 WHERE username = ?", (uid,))
    conn.commit()
    return {"ok": True}


def rotate_api_token(conn, user: dict) -> dict:
    return {"ok": True}


def audit_trail(conn, uid: str) -> dict:
    rows = conn.execute(
        "SELECT id, actor, action FROM audit WHERE actor = ? ORDER BY id", (uid,)
    ).fetchall()
    return {"items": [dict(r) for r in rows]}


def admin_dashboard(conn) -> dict:
    n_users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    n_reviews = conn.execute("SELECT COUNT(*) AS c FROM reviews").fetchone()["c"]
    n_approved = conn.execute("SELECT COUNT(*) AS c FROM reviews WHERE status = 'approved'").fetchone()["c"]
    n_flags = conn.execute("SELECT COUNT(*) AS c FROM reviews WHERE status = 'flagged'").fetchone()["c"]
    return {"n_users": n_users, "n_reviews": n_reviews, "n_approved": n_approved, "n_flags": n_flags}


def get_config(conn) -> dict:
    rows = conn.execute("SELECT key, value FROM config ORDER BY key").fetchall()
    return {r["key"]: r["value"] for r in rows}


def trigger_backup(conn) -> dict:
    return {"ok": True}