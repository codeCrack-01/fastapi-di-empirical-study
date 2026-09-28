"""ReviewGate-R — READ-ONLY route table (single source of truth for 12 endpoints).

The 12 read endpoints of the original 21-route app, verbatim in path, params,
auth level, and response model. The 9 write endpoints are absent by design.

The generator renders all 8 apps (4 patterns x sync/async) from this one table,
so no arm can drift from another on routes, auth, or models. A smoke test
asserts that every arm exposes exactly these 12 and nothing else.

Static (no-param) paths MUST precede parameterized paths so FastAPI resolves
them first.

auth: public | user | editor | admin   (role sets in core_read.ROLES)
sig:  inline handler params (FastAPI parses query/path)
call: argument expression passed to the shared service function
"""

from __future__ import annotations

from pydantic import BaseModel


# ---- response models (read-only subset of core/models.py) ----

class ReviewOut(BaseModel):
    id: int
    title: str
    body: str
    author: str
    status: str
    rating: int
    votes: int


class ReviewListOut(BaseModel):
    items: list[ReviewOut]
    total: int


class CommentOut(BaseModel):
    id: int
    review_id: int
    author: str
    body: str


class CommentListOut(BaseModel):
    items: list[CommentOut]


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str


class UserListOut(BaseModel):
    items: list[UserOut]


class ReviewStats(BaseModel):
    total: int
    approved: int
    flagged: int
    pending: int


class AuditOut(BaseModel):
    id: int
    actor: str
    action: str


class AuditListOut(BaseModel):
    items: list[AuditOut]


class DashboardOut(BaseModel):
    n_users: int
    n_reviews: int
    n_approved: int
    n_flags: int


class ConfigOut(BaseModel):
    max_editors: str
    backup_interval_h: str
    audit_enabled: str


class OkOut(BaseModel):
    ok: bool = True


# method, path, name, auth, service, response_model, sig, call
ROUTES_READ = [
    # --- static before parameterized ---
    ("GET", "/health", "health_check", "public", "health_check", OkOut,
     "", "(conn)"),
    ("GET", "/reviews", "list_reviews", "public", "list_reviews", ReviewListOut,
     "limit: int = 20, offset: int = 0", "(conn, limit, offset)"),
    ("GET", "/reviews/search", "search_reviews", "public", "search_reviews", ReviewListOut,
     "q: str, limit: int = 20", "(conn, q, limit)"),
    ("GET", "/reviews/stats", "review_stats", "public", "review_stats", ReviewStats,
     "", "(conn)"),
    ("GET", "/reviews/export", "export_reviews", "admin", "export_reviews", ReviewListOut,
     "", "(conn)"),
    ("GET", "/users/me", "my_profile", "user", "me", UserOut,
     "", "(conn, user)"),
    ("GET", "/users/admins", "list_admins", "user", "list_admins", UserListOut,
     "", "(conn)"),
    ("GET", "/admin/dashboard", "admin_dashboard", "admin", "admin_dashboard", DashboardOut,
     "", "(conn)"),
    ("GET", "/admin/config", "get_config", "admin", "get_config", ConfigOut,
     "", "(conn)"),
    ("GET", "/reviews/{rid}", "get_review", "public", "get_review", ReviewOut,
     "rid: int", "(conn, rid)"),
    ("GET", "/reviews/{rid}/comments", "list_comments", "public", "list_comments", CommentListOut,
     "rid: int", "(conn, rid)"),
    ("GET", "/users/{uid}/audit", "audit_trail", "admin", "audit_trail", AuditListOut,
     "uid: str", "(conn, uid)"),
]
