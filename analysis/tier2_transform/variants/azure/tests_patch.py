"""Convert azure S1/S3 test files from DI-overrides to app.state seeds.

Every `app.dependency_overrides[get_X] = lambda: V` site becomes
`app.state.<attr> = V`. Multi-line forms are handled (value continued
across lines, and the `= (lambda: ... )` wrapper).

For S3, bare-`FastAPI()` test apps additionally get
`ProvidersContextMiddleware` attached so `request.state` is populated.

Run from the arm root: MODE=s1|s3 .toolenv/bin/python
/path/to/variants/azure/tests_patch.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

GETTER_TO_STATE = {
    "get_app_settings": "settings",
    "get_user_id": "user_id",
    "get_credential_provider": "credential_provider",
    "get_credential": "credential",
    "get_llm_provider": "llm_provider",
    "get_search_provider": "search_provider",
    "get_database_client": "database_client",
    "get_agents_provider": "agents_provider",
    "get_content_safety_guard": "content_safety_guard",
    "get_post_prompt_validator": "post_prompt_validator",
    "get_runtime_overrides": "runtime_overrides",
}

TEST_FILES = [
    "tests/backend/test_admin.py",
    "tests/backend/test_conversation.py",
    "tests/backend/test_history.py",
    "tests/backend/test_health.py",
    "tests/backend/routers/test_speech.py",
    "tests/backend/routers/test_files.py",
]

MODE = os.environ.get("MODE", "s1").lower()

_OVERRIDE_PREFIX = re.compile(
    r"^(?P<ind>[ \t]*)(?P<app>\w+)\.dependency_overrides\[(?P<getter>\w+)\] = (?P<tail>.*)$"
)


def _depth(s: str) -> int:
    return s.count("(") + s.count("[") - s.count(")") - s.count("]")


def _eval_lambda(expr: str) -> str:
    """Evaluate a (possibly parameterized) lambda expression eagerly.

    `lambda: V` -> V ; `lambda n=name: body(n)` -> body(name). Seeded
    state must hold the resolved VALUE, not the callable.
    """
    expr = expr.strip()
    if expr.startswith("lambda: "):
        return expr[len("lambda: ") :]
    m = re.match(r"^lambda\s+([\w]+)=([^:]+):\s*(.*)$", expr, flags=re.DOTALL)
    if m:
        param, default, body = m.group(1), m.group(2).strip(), m.group(3)
        return re.sub(rf"\b{re.escape(param)}\b", default, body)
    return expr


def _rewrite(source: str) -> tuple[str, int]:
    raw = source.split("\n")
    out: list[str] = []
    n = 0
    i = 0
    while i < len(raw):
        line = raw[i]
        m = _OVERRIDE_PREFIX.match(line)
        if not m or m.group("getter") not in GETTER_TO_STATE:
            out.append(line)
            i += 1
            continue

        app = m.group("app")
        attr = GETTER_TO_STATE[m.group("getter")]
        tail = m.group("tail").strip()
        ind = m.group("ind")

        if tail == "(":
            # wrapper form:
            #   app.dependency_overrides[g] = (
            #       lambda: VALUE
            #   )
            body_lines: list[str] = []
            i += 1
            while i < len(raw) and raw[i].strip() != ")":
                body_lines.append(raw[i])
                i += 1
            i += 1  # consume the closing ')' line
            value = "\n".join(body_lines).strip()
            value = _eval_lambda(value)
            out.append(f"{ind}{app}.state.{attr} = {value}")
            n += 1
            continue

        if tail.startswith("lambda"):
            value = _eval_lambda(tail)
        else:
            out.append(line)
            i += 1
            continue

        # collect continuation lines until parens balance
        depth = _depth(value)
        while depth > 0 and i + 1 < len(raw):
            i += 1
            cont = raw[i]
            value += "\n" + cont.strip()
            depth += _depth(cont)
        out.append(f"{ind}{app}.state.{attr} = {value}")
        n += 1
        i += 1

    return "\n".join(out), n


def _attach_middleware(text: str) -> str:
    if not re.search(r" = FastAPI\(\)", text):
        return text
    if "ProvidersContextMiddleware" not in text:
        lines = text.split("\n")
        anchor = -1
        for idx, ln in enumerate(lines):
            if ln.startswith("from backend.dependencies import"):
                # advance past the parenthesized name block to its close
                anchor = idx
                if ln.rstrip().endswith("("):
                    j = idx + 1
                    while j < len(lines) and not lines[j].strip().endswith(")"):
                        j += 1
                    anchor = j
        lines.insert(anchor + 1, "from backend.middleware import ProvidersContextMiddleware")
        text = "\n".join(lines)
    text = re.sub(
        r"(?P<ind>[ \t]*)(?P<app>\w+) = FastAPI\(\)",
        lambda m: f"{m.group('ind')}{m.group('app')} = FastAPI()\n"
        f"{m.group('ind')}{m.group('app')}.add_middleware(ProvidersContextMiddleware)",
        text,
    )
    return text


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    total = 0
    for f in TEST_FILES:
        p = root / f
        if not p.exists():
            continue
        text, n = _rewrite(p.read_text())
        if MODE == "s3":
            text = _attach_middleware(text)
        p.write_text(text)
        total += n
        print(f"[{MODE}] rewrote {f}: {n} override sites")
    print(f"[{MODE}] total override sites converted: {total}")


if __name__ == "__main__":
    main()