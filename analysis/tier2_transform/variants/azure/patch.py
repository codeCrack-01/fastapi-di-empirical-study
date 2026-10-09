"""Build azure S1 or S3 arms from the S2 baseline (`main`).

S1 -- explicit imperative resolution: the 11 `*Dep = Annotated[..., Depends(...)]`
aliases are deleted from `backend.dependencies`; the 6 routers' handlers drop
all alias params and resolve providers by calling the deps.py resolvers
directly (`get_database_client(request)`, `resolve_settings(request)`, ...).

S3 -- ambient request state: `backend.middleware.ProvidersContextMiddleware`
(registered in `create_app`) copies `app.state` into `request.state` and
materializes the per-request guard/validator; handlers read
`request.state.<key>`.

Both arms keep the getter functions themselves (seam tests in
test_dependencies.py call them directly with fake requests), so only the
dependency-overrides-based *test* overrides need converting to `app.state`
seeds -- that's `variants/azure/tests_patch.py`.

Usage: MODE=s1 (or s3) .toolenv/bin/python variants/azure/patch.py .
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import libcst as cst

ROUTERS = ["admin.py", "conversation.py", "files.py", "health.py", "history.py", "speech.py"]

ALIASES = {
    "SettingsDep",
    "CredentialProviderDep",
    "CredentialDep",
    "LLMProviderDep",
    "SearchProviderDep",
    "DatabaseClientDep",
    "AgentsProviderDep",
    "ContentSafetyGuardDep",
    "RuntimeOverridesDep",
    "PostPromptValidatorDep",
    "UserIdDep",
}

S1_RESOLVER = {
    "SettingsDep": "resolve_settings",
    "UserIdDep": "resolve_user_id",
    "CredentialProviderDep": "get_credential_provider",
    "CredentialDep": "get_credential",
    "LLMProviderDep": "get_llm_provider",
    "SearchProviderDep": "get_search_provider",
    "DatabaseClientDep": "get_database_client",
    "AgentsProviderDep": "get_agents_provider",
    "RuntimeOverridesDep": "get_runtime_overrides",
    "ContentSafetyGuardDep": "get_content_safety_guard",
    "PostPromptValidatorDep": "resolve_post_prompt_validator",
}

STATE_KEY = {
    "SettingsDep": "settings",
    "UserIdDep": "user_id",
    "CredentialProviderDep": "credential_provider",
    "CredentialDep": "credential",
    "LLMProviderDep": "llm_provider",
    "SearchProviderDep": "search_provider",
    "DatabaseClientDep": "database_client",
    "AgentsProviderDep": "agents_provider",
    "RuntimeOverridesDep": "runtime_overrides",
    "ContentSafetyGuardDep": "content_safety_guard",
    "PostPromptValidatorDep": "post_prompt_validator",
}

BIND_ORDER = [
    "SettingsDep",
    "UserIdDep",
    "CredentialProviderDep",
    "CredentialDep",
    "LLMProviderDep",
    "SearchProviderDep",
    "DatabaseClientDep",
    "AgentsProviderDep",
    "RuntimeOverridesDep",
    "ContentSafetyGuardDep",
    "PostPromptValidatorDep",
]

MODE = os.environ.get("MODE", "s1").lower()


def _annotation_name(node: cst.Param) -> str | None:
    ann = getattr(node.annotation, "annotation", None)
    if isinstance(ann, cst.Name):
        return ann.value
    return None


def _make_assign(target: str, rhs: str) -> cst.SimpleStatementLine:
    return cst.SimpleStatementLine(
        body=[
            cst.Assign(
                targets=[cst.AssignTarget(target=cst.Name(target))],
                value=cst.parse_expression(rhs),
            )
        ]
    )


class _RouterTransformer(cst.CSTTransformer):
    """Pass 1: rewrite handler signatures + insert bindings.

    Collects the names the handlers now need from `backend.dependencies`
    into `needed_deps` for pass 2's import fixup.
    """

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.needed_deps: list[str] = []
        self.handlers_with_aliases = False

    def leave_FunctionDef(self, orig, updated):
        kept: list[cst.Param] = []
        removed: list[tuple[str, str]] = []
        for p in orig.params.params:
            a = _annotation_name(p)
            if a in ALIASES:
                removed.append((p.name.value, a))
                self.handlers_with_aliases = True
            else:
                kept.append(p)
        if not removed:
            return updated

        if self.mode == "s1":
            for _, a in removed:
                fn = S1_RESOLVER[a]
                if fn not in self.needed_deps:
                    self.needed_deps.append(fn)

        removed_names = {a for _, a in removed}
        has_request = any(p.name.value == "request" for p in kept)
        new_params = list(kept)
        if not has_request:
            new_params.insert(
                0,
                cst.Param(
                    name=cst.Name("request"),
                    annotation=cst.Annotation(annotation=cst.Name("Request")),
                ),
            )
        new_params = tuple(new_params)

        local = {a: n for n, a in removed}
        settings_n = local.get("SettingsDep", "settings")
        llm_n = local.get("LLMProviderDep", "llm")
        ovr_n = local.get("RuntimeOverridesDep", "overrides")

        stmts: list[cst.BaseStatement] = []
        for a in BIND_ORDER:
            if a not in removed_names:
                continue
            n = local[a]
            if self.mode == "s1":
                if a == "SettingsDep":
                    rhs = f"{n} = resolve_settings(request)"
                elif a == "UserIdDep":
                    rhs = f"{n} = resolve_user_id(request)"
                elif a == "ContentSafetyGuardDep":
                    rhs = (
                        f"{n} = get_content_safety_guard(request, {settings_n})"
                        if "SettingsDep" in removed_names
                        else f"{n} = get_content_safety_guard(request, resolve_settings(request))"
                    )
                elif a == "PostPromptValidatorDep":
                    rhs = f"{n} = resolve_post_prompt_validator(request, {llm_n}, {ovr_n})"
                else:
                    rhs = f"{n} = {S1_RESOLVER[a]}(request)"
            else:
                rhs = f"{n} = request.state.{STATE_KEY[a]}"
            target, expr = rhs.split(" = ", 1)
            stmts.append(_make_assign(target, expr))
        if not stmts:
            return updated

        body = updated.body
        lst = list(body.body)
        ins_at = 0
        if lst and isinstance(lst[0], cst.SimpleStatementLine):
            first = lst[0].body[0]
            if isinstance(first, cst.Expr) and isinstance(first.value, cst.SimpleString):
                ins_at = 1
        lst[ins_at:ins_at] = stmts

        return updated.with_changes(
            params=updated.params.with_changes(params=new_params),
            body=body.with_changes(body=lst),
        )


class _ImportFixer(cst.CSTTransformer):
    """Pass 2: prune alias names from the backend.dependencies import.

    Uses the `needed_deps` collected by pass 1.
    """

    def __init__(self, mode: str, needed: list[str]) -> None:
        self.mode = mode
        self.needed = needed
        self.added = False

    def leave_ImportFrom(self, orig, updated) -> cst.CSTNode:
        if not orig.module or _full_name(orig.module) != "backend.dependencies":
            return updated
        if not self.needed and not any(_annotation_name_in_alias(ia) for ia in orig.names):
            return updated  # nothing DI-related to prune
        kept: list[cst.ImportAlias] = []
        seen: set[str] = set()
        new_names = (
            [cst.ImportAlias(name=cst.Name(n)) for n in self.needed] if self.mode == "s1" else []
        )
        for ia in new_names:
            seen.add(ia.name.value)
        for ia in orig.names:
            v = ia.name.value
            if v in ALIASES:
                continue
            if v in seen:
                continue
            seen.add(v)
            kept.append(ia)
        if not kept and not new_names:
            return cst.RemoveFromParent()
        return updated.with_changes(names=tuple(kept) + tuple(new_names))


def _annotation_name_in_alias(node: cst.ImportAlias) -> bool:
    return isinstance(node.name, cst.Name) and node.name.value in ALIASES


def _full_name(node: cst.BaseExpression) -> str:
    if isinstance(node, cst.Name):
        return node.value
    if isinstance(node, cst.Attribute):
        return f"{_full_name(node.value)}.{node.attr.value}"
    return node.__class__.__name__


def _ensure_request_import(text: str) -> str:
    if "import Request" in text:
        return text
    lines = text.split("\n")
    first_import = 0
    for idx, line in enumerate(lines):
        if line.startswith(("import ", "from ")):
            first_import = idx
            break
    lines.insert(first_import, "from fastapi import Request")
    return "\n".join(lines)


def _patch_deps(deps: Path) -> None:
    src = deps.read_text()

    def _strip_aliases(src: str) -> str:
        for pattern in (
            r"^([A-Za-z]+Dep) = Annotated\[\n(?:[ \t].*\n)+?\]\n",
            r"^([A-Za-z]+Dep) = Annotated\[[^\n]*\]\n",
        ):
            src = re.sub(pattern, "", src, flags=re.MULTILINE)
        return src

    src = _strip_aliases(src)

    src = src.replace("settings: SettingsDep,", "settings: AppSettings,")
    src = src.replace("llm: LLMProviderDep,", "llm: BaseLLMProvider,")
    src = src.replace("overrides: RuntimeOverridesDep,", "overrides: RuntimeConfig | None,")

    src = src.replace("from fastapi import Depends, Request", "from fastapi import Request")
    src = re.sub(r"^from typing import Annotated[^\n]*\n", "", src, flags=re.MULTILINE)

    old = (
        "Single source of truth for how routers obtain settings, credentials,\n"
        "and providers. Routers MUST go through `Depends(...)` -- no module-\n"
        "level singletons, no env-var reads inside route handlers."
    )
    new = (
        "Single source of truth for how routers obtain settings, credentials,\n"
        "and providers."
    )
    if old in src:
        src = src.replace(old, new)

    guard_anchor = '    client = getattr(request.app.state, "content_safety_client", None)\n'
    seam = (
        '    seeded = getattr(request.app.state, "content_safety_guard", None)\n'
        "    if seeded is not None:\n"
        "        return seeded\n"
        '    client = getattr(request.app.state, "content_safety_client", None)\n'
    )
    assert guard_anchor in src, "guard anchor missing"
    src = src.replace(guard_anchor, seam, 1)

    helpers = '''

def resolve_settings(request: Request) -> AppSettings:
    """Return settings: a test-seeded `app.state.settings`, else the env default."""
    app = getattr(request, "app", None)
    if app is not None:
        seeded = getattr(getattr(app, "state", None), "settings", None)
        if seeded is not None:
            return seeded
    return get_app_settings()


def resolve_user_id(request: Request) -> str:
    """Return the caller id: a test-seeded `app.state.user_id`, else the header read."""
    app = getattr(request, "app", None)
    if app is not None:
        seeded = getattr(getattr(app, "state", None), "user_id", None)
        if seeded is not None:
            return seeded
    return get_user_id(request)


def resolve_post_prompt_validator(
    request: Request,
    llm: BaseLLMProvider,
    overrides: RuntimeConfig | None,
) -> PostPromptValidator | None:
    """Return a test-seeded `app.state.post_prompt_validator`, else build one."""
    app = getattr(request, "app", None)
    if app is not None:
        seeded = getattr(getattr(app, "state", None), "post_prompt_validator", None)
        if seeded is not None:
            return seeded
    return build_post_prompt_validator(llm, overrides)


'''
    marker = "__all__ = ["
    assert marker in src, "__all__ marker missing"
    src = src.replace(marker, helpers + marker, 1)

    new_all = [
        '"get_agents_provider"',
        '"get_app_settings"',
        '"get_content_safety_guard"',
        '"get_credential"',
        '"get_credential_provider"',
        '"get_database_client"',
        '"get_llm_provider"',
        '"get_post_prompt_validator"',
        '"get_runtime_overrides"',
        '"get_search_provider"',
        '"get_user_id"',
        '"resolve_post_prompt_validator"',
        '"resolve_settings"',
        '"resolve_user_id"',
    ]
    block = "__all__ = [\n" + "".join(f"    {n},\n" for n in new_all) + "]\n"
    i = src.find("__all__ = [")
    src = src[:i] + block
    deps.write_text(src)
    print(f"[{MODE}] patched {deps}")


def _patch_app_s3() -> None:
    app_py = Path("src/backend/app.py")
    src = app_py.read_text()
    anchor = "    install_exception_handlers(app)\n    return app\n"
    assert anchor in src, "create_app tail anchor missing"
    src = src.replace(
        anchor,
        "    install_exception_handlers(app)\n"
        "    app.add_middleware(ProvidersContextMiddleware)\n"
        "    return app\n",
        1,
    )
    src = src.replace(
        "from backend.routers import admin, conversation, files, health, history, speech",
        "from backend.routers import admin, conversation, files, health, history, speech\n"
        "from backend.middleware import ProvidersContextMiddleware",
        1,
    )
    app_py.write_text(src)
    print(f"[{MODE}] patched app.py")


_S3_MIDDLEWARE = '''"""S3 arm: per-request provider state.

`ProvidersContextMiddleware` materializes every provider/config value the
routers need into `request.state` before the route runs: singletons are
copied from `app.state` (seeded by the lifespan or, in tests, directly),
and the per-request guards are built once per request. Routers read
`request.state.<key>` and never call a resolver themselves.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.dependencies import (
    get_content_safety_guard,
    resolve_post_prompt_validator,
    resolve_settings,
    resolve_user_id,
)

_COPIED_KEYS = (
    "credential_provider",
    "credential",
    "llm_provider",
    "agents_provider",
    "database_client",
    "search_provider",
    "runtime_overrides",
    "content_safety_client",
)


class ProvidersContextMiddleware(BaseHTTPMiddleware):
    """Seed `request.state` from `app.state` plus per-request builds."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        app_state = request.app.state
        for key in _COPIED_KEYS:
            if hasattr(app_state, key):
                setattr(request.state, key, getattr(app_state, key))
            else:
                # optional providers default to None (matches the getters'
                # tolerant semantics); mandatory ones surface late as the
                # handler touches them, mirroring the S2/S1 500 path.
                setattr(request.state, key, None)

        request.state.settings = getattr(app_state, "settings", None) or resolve_settings(
            request
        )
        request.state.user_id = resolve_user_id(request)
        request.state.content_safety_guard = (
            getattr(app_state, "content_safety_guard", None)
            or get_content_safety_guard(request, request.state.settings)
        )
        request.state.post_prompt_validator = (
            getattr(app_state, "post_prompt_validator", None)
            or resolve_post_prompt_validator(
                request,
                getattr(app_state, "llm_provider", None),
                getattr(app_state, "runtime_overrides", None),
            )
        )
        return await call_next(request)


__all__ = ["ProvidersContextMiddleware"]
'''


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    routers_dir = root / "src" / "backend" / "routers"

    for fn in ROUTERS:
        p = routers_dir / fn
        if not p.exists():
            continue
        tree = cst.parse_module(p.read_text())
        pass1 = _RouterTransformer(MODE)
        intermediate = tree.visit(pass1)
        pass2 = _ImportFixer(MODE, pass1.needed_deps)
        final = intermediate.visit(pass2)
        text = final.code
        text = _ensure_request_import(text)
        p.write_text(text)
        if pass1.handlers_with_aliases:
            print(f"[{MODE}] patched routers/{fn}")

    _patch_deps(root / "src" / "backend" / "dependencies.py")
    if MODE == "s3":
        mw = root / "src" / "backend" / "middleware.py"
        mw.write_text(_S3_MIDDLEWARE)
        print(f"[{MODE}] wrote backend/middleware.py")
        _patch_app_s3()


if __name__ == "__main__":
    main()