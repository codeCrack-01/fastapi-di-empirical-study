"""Transform vstorm-co server.py from S2 (FastAPI Depends) to S1 (no DI).

S1 contract: guards that ran through `Depends` become explicit calls in the
handler body; no `Depends(...)` remains in the file. Work equivalence: the
same `service.check_service_token(token)` / `service.check_session_token(...)`
calls run on exactly the routes that had `dependencies=[ServiceAuth]` and
`session_id: AuthorizedSession`.

Usage: <toolenv>/bin/python s1_patch.py <path/to/server.py>
"""

import sys

import libcst as cst
import libcst.matchers as m

GUARD_FUNCS = {"_service_of", "_require_service_token", "_authorized_session"}
DROP_ALIASES = {"ServiceDep", "ServiceAuth", "AuthorizedSession"}
SESSION_ANNOTATION = "Annotated[str, PathParam(pattern=wire.SESSION_ID_PATTERN)]"

MODE = __import__("os").environ.get("MODE", "s1")  # "s1" or "s3"

MIDDLEWARE = '''
    @app.middleware("http")
    async def ambient_auth(request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
        """S3: ambient auth context applied once, before routing (no DI parameters)."""
        try:
            path = request.url.path
            if path not in ("/", "/ui", "/healthz"):
                token = request.headers.get(wire.TOKEN_HEADER)
                prefix = "/sessions/"
                if path.startswith(prefix):
                    rest = path[len(prefix):]
                    session_id = rest.split("/", 1)[0]
                    if re.fullmatch(wire.SESSION_ID_PATTERN, session_id):
                        service.check_session_token(session_id, token)
                        return await call_next(request)
                service.check_service_token(token)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        return await call_next(request)

'''

prologue_hits = []



def _code(node: cst.CSTNode) -> str:
    return cst.parse_module("").code_for_node(node)

def _ann_code(param: cst.Param) -> str | None:
    if param.annotation is None:
        return None
    return _code(param.annotation.annotation)


def _is_docstring(stmt: cst.BaseStatement) -> bool:
    if isinstance(stmt, (cst.SimpleStatementLine, cst.SimpleStatementSuite)):
        return m.matches(stmt, m.SimpleStatementLine(body=[m.Expr(m.SimpleString())])) or m.matches(
            stmt, m.SimpleStatementSuite(body=[m.Expr(m.SimpleString())])
        )
    return False


def _insert_prologue(body: cst.IndentedBlock, stmt: cst.BaseStatement) -> cst.IndentedBlock:
    body_list = list(body.body)
    if body_list and _is_docstring(body_list[0]):
        body_list[1:1] = [stmt]
    else:
        body_list[0:0] = [stmt]
    return body.with_changes(body=body_list)


def _drop_service_auth_from_decorator(decorator: cst.Decorator) -> cst.Decorator | None:
    """Remove ServiceAuth from dependencies=[...]; return None if decorator gone."""
    call = decorator.decorator
    if not isinstance(call, cst.Call):
        return decorator
    new_args = []
    changed = False
    for arg in call.args:
        if arg.keyword and arg.keyword.value == "dependencies" and isinstance(arg.value, cst.List):
            kept = [e for e in arg.value.elements if _code(e.value) != "ServiceAuth"]
            if len(kept) != len(arg.value.elements):
                changed = True
                if kept:
                    new_args.append(arg.with_changes(value=arg.value.with_changes(elements=kept)))
                continue
        new_args.append(arg)
    if not changed:
        return decorator
    return decorator.with_changes(decorator=call.with_changes(args=new_args))


class Transform(cst.CSTTransformer):
    # ---- params -------------------------------------------------------
    def leave_Param(self, orig: cst.Param, updated: cst.Param) -> cst.Param | cst.RemovalSentinel:
        code = _ann_code(updated)
        if code == "AuthorizedSession":
            return updated.with_changes(
                annotation=cst.Annotation(annotation=cst.parse_expression(SESSION_ANNOTATION))
            )
        if code == "ServiceDep":
            return cst.RemoveFromParent()
        return updated

    # ---- functions ----------------------------------------------------
    def leave_FunctionDef(self, orig: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        if orig.name.value in GUARD_FUNCS:
            return updated  # module-level pass removes these

        decs = list(updated.decorators)
        had_service_auth = False
        new_decs = []
        for d in decs:
            call = d.decorator
            if isinstance(call, cst.Call) and any(
                arg.keyword and arg.keyword.value == "dependencies" and "ServiceAuth" in _code(arg.value)
                for arg in call.args
            ):
                had_service_auth = True
                d2 = _drop_service_auth_from_decorator(d)
                if d2 is not None:
                    new_decs.append(d2)
                continue
            new_decs.append(d)

        params = list(updated.params.params)
        # detect on the ORIGINAL node: child params were already rewritten
        orig_codes = [_ann_code(p) for p in orig.params.params]
        needs_session = "AuthorizedSession" in orig_codes
        needs_service = had_service_auth or "ServiceDep" in orig_codes

        if not (needs_session or needs_service):
            return updated.with_changes(decorators=new_decs)

        if MODE == "s3":
            updated = updated.with_changes(decorators=new_decs)
            if "AuthorizedSession" in orig_codes:
                prologue_hits.append((orig.name.value, "session(ambient)"))
            elif had_service_auth:
                prologue_hits.append((orig.name.value, "service(ambient)"))
            return updated

        names = [p.name.value for p in params]
        if "token" not in names:
            params.append(
                cst.Param(
                    name=cst.Name("token"),
                    annotation=cst.Annotation(annotation=cst.parse_expression("TokenHeader")),
                    default=cst.Name("None"),
                )
            )
        if needs_session:
            stmt_text = "service.check_session_token(session_id, token)"
            kind = "session"
        else:
            stmt_text = "service.check_service_token(token)"
            kind = "service"
        prologue_hits.append((orig.name.value, kind))
        updated = updated.with_changes(
            decorators=new_decs,
            params=updated.params.with_changes(params=params),
            body=_insert_prologue(updated.body, cst.parse_statement(stmt_text)),
        )
        return updated

    # ---- module level -------------------------------------------------
    def leave_SimpleStatementLine(self, orig, updated):
        for stmt in updated.body:
            if isinstance(stmt, cst.Assign) and any(
                isinstance(t.target, cst.Name) and t.target.value in DROP_ALIASES
                for t in stmt.targets
            ):
                return cst.RemoveFromParent()
        return updated

    def leave_Module(self, orig: cst.Module, updated: cst.Module) -> cst.Module:
        body = [
            s
            for s in updated.body
            if not (isinstance(s, cst.FunctionDef) and s.name.value in GUARD_FUNCS)
        ]
        return updated.with_changes(body=body)


def drop_depends_import(tree: cst.Module) -> cst.Module:
    new_body = []
    for stmt in tree.body:
        if isinstance(stmt, cst.SimpleStatementLine):
            rewritten = False
            for imp in stmt.body:
                if isinstance(imp, cst.ImportFrom) and imp.module and _code(imp.module) == "fastapi":
                    names = [a for a in imp.names if a.name.value != "Depends"]
                    if len(names) != len(imp.names):
                        rewritten = True
                        if not names:
                            stmt = None
                        else:
                            stmt = stmt.with_changes(body=[imp.with_changes(names=names)])
            if stmt is None:
                continue
            del rewritten
        new_body.append(stmt)
    return tree.with_changes(body=new_body)


def main(path: str) -> None:
    src = open(path).read()
    out = cst.parse_module(src).visit(Transform())
    out = drop_depends_import(out)
    code = out.code
    if MODE == "s3":
        needle = 'def _register_session_routes(app: FastAPI, service: _Service) -> None:'
        idx = code.index(needle) + len(needle)
        code = code[:idx] + MIDDLEWARE + code[idx:]
        code = code.replace(
            "from fastapi.responses import HTMLResponse",
            "from fastapi.responses import HTMLResponse, JSONResponse",
        )
    leftover = [f"{i}: {l}" for i, l in enumerate(code.splitlines(), 1) if "Depends" in l]
    if leftover:
        print("WARNING Depends still present:", file=sys.stderr)
        print("\n".join(leftover), file=sys.stderr)
    open(path, "w").write(code)
    print(f"patched {path}  ({len(prologue_hits)} handlers)")
    for name, kind in prologue_hits:
        print(f"  {kind:8} {name}")


if __name__ == "__main__":
    main(sys.argv[1])
