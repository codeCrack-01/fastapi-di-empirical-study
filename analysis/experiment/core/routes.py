"""ReviewGate — route table (single source of truth for the 20 endpoints).

Each entry fully describes the endpoint. The strategy generator renders the
handler bodies from this table, so all four strategies expose identical
routes, params, auth levels, and response models.

IMPORTANT: static (no-param) paths MUST be listed before parameterized paths so
that FastAPI route matching resolves them first.

auth: public | user | editor | admin  (role sets in core/auth.ROLES)
sig:  inline handler parameter signature (FastAPI parses query/body/path)
call: argument expression passed to the shared service function
"""

from __future__ import annotations

from . import models as m

ROUTES = [
    # method, path, name, auth, service, response_model, sig, call
    ("GET", "/reviews", "list_reviews", "public", "list_reviews", m.ReviewListOut,
     "limit: int = 20, offset: int = 0", "(conn, limit, offset)"),
    ("GET", "/reviews/search", "search_reviews", "public", "search_reviews", m.ReviewListOut,
     "q: str, limit: int = 20", "(conn, q, limit)"),
    ("GET", "/reviews/stats", "review_stats", "public", "review_stats", m.ReviewStats,
     "", "(conn)"),
    ("GET", "/reviews/export", "export_reviews", "admin", "export_reviews", m.ReviewListOut,
     "", "(conn)"),
    ("GET", "/users/me", "my_profile", "user", "me", m.UserOut,
     "", "(conn, user)"),
    ("GET", "/users/admins", "list_admins", "user", "list_admins", m.UserListOut,
     "", "(conn)"),
    ("POST", "/users/me/api-token", "rotate_token", "user", "rotate_api_token", m.OkOut,
     "", "(conn, user)"),
    ("GET", "/admin/dashboard", "admin_dashboard", "admin", "admin_dashboard", m.DashboardOut,
     "", "(conn)"),
    ("GET", "/admin/config", "get_config", "admin", "get_config", m.ConfigOut,
     "", "(conn)"),
    ("POST", "/admin/backup", "trigger_backup", "admin", "trigger_backup", m.OkOut,
     "", "(conn)"),

    ("POST", "/reviews", "create_review", "editor", "create_review", m.ReviewOut,
     "body: m.ReviewIn", "(conn, body.title, body.body, body.rating, user)"),
    ("GET", "/reviews/{rid}", "get_review", "public", "get_review", m.ReviewOut,
     "rid: int", "(conn, rid)"),
    ("GET", "/reviews/{rid}/comments", "list_comments", "public", "list_comments", m.CommentListOut,
     "rid: int", "(conn, rid)"),
    ("POST", "/reviews/{rid}/votes", "vote", "user", "vote", m.ReviewOut,
     "rid: int, body: m.VoteIn", "(conn, rid, body.value, user)"),
    ("POST", "/reviews/{rid}/flag", "flag_review", "editor", "flag_review", m.ReviewOut,
     "rid: int", "(conn, rid, user)"),
    ("POST", "/reviews/{rid}/approve", "approve_review", "admin", "approve_review", m.ReviewOut,
     "rid: int", "(conn, rid, user)"),
    ("PATCH", "/reviews/{rid}", "update_review", "editor", "update_review", m.ReviewOut,
     "rid: int, body: m.ReviewIn", "(conn, rid, body, user)"),
    ("DELETE", "/reviews/{rid}", "delete_review", "editor", "delete_review", m.OkOut,
     "rid: int", "(conn, rid, user)"),
    ("POST", "/users/{uid}/suspend", "suspend_user", "admin", "suspend_user", m.OkOut,
     "uid: str", "(conn, uid, user)"),
    ("GET", "/users/{uid}/audit", "audit_trail", "admin", "audit_trail", m.AuditListOut,
     "uid: str", "(conn, uid)"),
]