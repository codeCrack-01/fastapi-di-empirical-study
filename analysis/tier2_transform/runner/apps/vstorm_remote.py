"""Bench-side ASGI entry for the vstorm remote server (NOT part of any repo).

The DI transformation for vstorm lands in
src/pydantic_ai_backends/remote/server.py, which ships a create_app(config)
factory rather than a module-level app. uvicorn needs an import string, so the
bench builds the app here: token "bench-token", a one-entry runtime allowlist,
no Docker calls at import (sandboxes are only built when a session is opened).

The route measured is GET /sessions (ServiceAuth -> ServiceDep DI graph).
"""

import sys
from pathlib import Path

REPO_SRC = Path(__file__).resolve().parents[2] / "repos" / "vstorm-co" / "src"
sys.path.insert(0, str(REPO_SRC))

from pydantic_ai_backends.remote.server import SandboxdConfig, create_app  # noqa: E402

app = create_app(
    SandboxdConfig(
        token="bench-token",
        runtimes={"python": "python:3.12-slim"},
        default_runtime="python",
    )
)