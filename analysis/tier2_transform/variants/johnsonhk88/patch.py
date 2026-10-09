"""johnsonhk88 arm builder: S1 (imperative) and S3 (middleware + request.state).

Repo shape (app/deps.py): `get_db` (session, from `_get_session`) and
`get_current_user` (bearer + session). Handlers take
`db: AsyncSession = Depends(get_db)` and/or
`current_user: User = Depends(get_current_user)`.

Both arms replace the Depends graph with app.state-seeded seams:

  - db_scope(request)      -- app.state.db seed wins, else a real AsyncSession
                              (matched close on exit; pool-safe).
  - resolve_current_user(request, db) -- app.state.current_user seed wins, else
                              bearer auth against `db`.

S1: handlers open the session themselves and auth explicitly:
    async with db_scope(request) as db:
        current_user = await resolve_current_user(request, db)
        <body>

S3: a BaseHTTPMiddleware owns db_scope for the whole request and stashes the
session on request.state; handlers only read it:
    db = request.state.db
    current_user = await resolve_current_user(request, db)
    <body>

Both arms keep behavior byte-identical (same DB work, same auth). Tests need
no changes: the 12-test gate never used dependency_overrides.

Usage (from the repo root, api/):  python variants/johnsonhk88/patch.py s1|s3
"""

from __future__ import annotations

import ast
import re
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent / "repos" / "johnsonhk88"
API = REPO / "api"

RANGERS = ["app/api/auth.py", "app/api/documents.py", "app/api/agent_runs.py"]

DEP_PARAMS = ("db", "current_user")

DEPS_V1 = '''\
from contextlib import asynccontextmanager

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.models import User

bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def db_scope(request: Request):
    seeded = getattr(request.app.state, "db", None)
    if seeded is not None:
        yield seeded
        return
    async with AsyncSessionLocal() as session:
        yield session


async def _authenticate(creds, db: AsyncSession) -> User:
    if not creds:
        raise HTTPException(401, detail={"error": {"code": "UNAUTHORIZED", "message": "Missing token"}})
    payload = decode_access_token(creds.credentials)
    if not payload:
        raise HTTPException(401, detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid token"}})
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, detail={"error": {"code": "UNAUTHORIZED", "message": "User not found"}})
    return user


async def resolve_current_user(request: Request, db: AsyncSession | None = None) -> User:
    seeded = getattr(request.app.state, "current_user", None)
    if seeded is not None:
        return seeded
    creds = await bearer(request)
    if db is None:
        async with db_scope(request) as sess:
            return await _authenticate(creds, sess)
    return await _authenticate(creds, db)
'''

MIDDLEWARE = '''\
"""S3 arm: per-request provider state.

`ProvidersContextMiddleware` opens one session (seeded or real) for the whole
request and stashes it on `request.state.db`; routers read it directly and
never call a resolver. Session close is owned by the middleware's `async with`.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from app.deps import db_scope


class ProvidersContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        async with db_scope(request) as db:
            request.state.db = db
            response = await call_next(request)
            return response
'''

MAIN_S3_PATCH = (
    'from app.middleware import ProvidersContextMiddleware\n',
    'app.add_middleware(ProvidersContextMiddleware)\n',
)


def _split_args(s: str) -> list[str]:
    """Split a parameter list on top-level commas (paren/bracket aware)."""
    parts, depth, buf = [], 0, []
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def _dedent_keep(s: str) -> str:
    return textwrap.dedent(s.rstrip("\n"))


class _Handler:
    """A single FastAPI handler and its rewrite plan."""

    def __init__(self, node: ast.AsyncFunctionDef):
        self.node = node
        # param name -> is-present marker for the two DI params
        self.has_db = any(a.arg == "db" for a in node.args.args)
        self.has_user = any(a.arg == "current_user" for a in node.args.args)

    @property
    def params(self) -> list[ast.arg]:
        return list(self.node.args.args)


def _param_default(node: ast.AsyncFunctionDef, arg: ast.arg) -> str | None:
    """Return unparsed default for `arg` in node.args (positional defaults)."""
    d = node.args.defaults
    idx = _arg_index(node, arg)
    if idx is None:
        return None
    ndefs = len(node.args.args) - len(d)
    pos = idx - ndefs
    if 0 <= pos < len(d):
        return ast.unparse(d[pos])
    return None


def _arg_index(node: ast.AsyncFunctionDef, arg: ast.arg) -> int | None:
    for i, a in enumerate(node.args.args):
        if a.arg == arg.arg:
            return i
    return None


def _rebuilt_signature(node: ast.AsyncFunctionDef) -> str:
    keep, keep_defaults, no_defaults_after = [], [], False
    for a in node.args.args:
        if a.arg in DEP_PARAMS:
            continue
        default = _param_default(node, a)
        piece = a.arg
        if a.annotation:
            piece += ": " + ast.unparse(a.annotation)
        if default is not None:
            piece += f" = {default}"
        else:
            no_defaults_after = True
        keep.append(piece)
    ret = ": " + ast.unparse(node.returns) if node.returns else ""
    name = node.name
    body = f"request: Request, {', '.join(keep)}" if keep else "request: Request"
    return f"async def {name}({body}){ret}:"


def _original_body_inner(node: ast.AsyncFunctionDef, src_lines: list[str]) -> str:
    start = node.body[0].lineno
    end = node.end_lineno
    body = "\n".join(src_lines[start - 1 : end])
    return _dedent_keep(body)


def rewrite_file(path: Path, mode: str) -> None:
    src = path.read_text()
    tree = ast.parse(src)
    src_lines = src.split("\n")

    edits: list[tuple[int, int, str]] = []  # (start_line, end_line, replacement)
    for module_node in ast.walk(tree):
        for child in ast.iter_child_nodes(module_node):
            if isinstance(child, ast.AsyncFunctionDef) and child.body:
                h = _Handler(child)
                if not (h.has_db or h.has_user):
                    continue
                header = _rebuilt_signature(child)
                body_inner = _original_body_inner(child, src_lines)
                ind8 = textwrap.indent(body_inner, "        ")
                if mode == "s1":
                    prolog = "    async with db_scope(request) as db:\n"
                    if h.has_user:
                        prolog += (
                            "        current_user = await "
                            "resolve_current_user(request, db)\n"
                        )
                    new = header + "\n" + prolog + ind8 + "\n"
                else:
                    ind4 = textwrap.indent(body_inner, "    ")
                    prolog = "    db = request.state.db\n"
                    if h.has_user:
                        prolog += (
                            "    current_user = await "
                            "resolve_current_user(request, db)\n"
                        )
                    new = header + "\n" + prolog + ind4 + "\n"
                start = child.lineno
                end = child.end_lineno
                edits.append((start, end, new))

    for start, end, new in sorted(edits, key=lambda e: e[0], reverse=True):
        src_lines = src_lines[: start - 1] + new.split("\n") + src_lines[end:]

    out = "\n".join(src_lines)

    # import fix-ups (harmless to keep unused model imports; pytest gate)
    out = out.replace(
        "from app.deps import get_db, get_current_user",
        "from app.deps import db_scope, resolve_current_user",
    )
    out = out.replace(
        "from fastapi import APIRouter, Depends, File, HTTPException, UploadFile",
        "from fastapi import APIRouter, File, HTTPException, Request, UploadFile",
    )
    out = out.replace(
        "from fastapi import APIRouter, Depends, HTTPException, Query",
        "from fastapi import APIRouter, HTTPException, Query, Request",
    )
    out = out.replace(
        "from fastapi import APIRouter, Depends, HTTPException",
        "from fastapi import APIRouter, HTTPException, Request",
    )
    path.write_text(out)


def attach_middleware(mode: str) -> None:
    if mode != "s3":
        return
    main = API / "app" / "main.py"
    src = main.read_text()
    if "ProvidersContextMiddleware" in src:
        return
    src = src.replace(
        "from app.config import settings\n",
        "from app.config import settings\nfrom app.middleware import ProvidersContextMiddleware\n",
    )
    src = src.replace(
        "app.add_middleware(CORSMiddleware, allow_origins=[\"http://localhost:5173\"]"
        " if settings.APP_ENV == \"dev\" else [], allow_credentials=True,"
        " allow_methods=[\"*\"], allow_headers=[\"*\"])",
        "app.add_middleware(CORSMiddleware, allow_origins=[\"http://localhost:5173\"]"
        " if settings.APP_ENV == \"dev\" else [], allow_credentials=True,"
        " allow_methods=[\"*\"], allow_headers=[\"*\"])\n\n"
        "app.add_middleware(ProvidersContextMiddleware)",
    )
    main.write_text(src)
    (API / "app" / "middleware.py").write_text(MIDDLEWARE)


def patch_arms(mode: str) -> None:
    assert mode in ("s1", "s3"), mode
    deps = API / "app" / "deps.py"
    deps.write_text(DEPS_V1)
    for rel in RANGERS:
        rewrite_file(API / rel, mode)
    attach_middleware(mode)


if __name__ == "__main__":
    patch_arms(sys.argv[1])
    print(f"patched johnsonhk88 {sys.argv[1]}")