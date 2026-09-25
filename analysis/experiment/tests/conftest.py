"""ReviewGate functional-equivalence harness (pytest).

Boots each strategy app in isolation with a private temp SQLite DB so all four
variants observe identical seed state. Exposes one module-scoped TestClient
fixture per strategy.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

STRATEGIES = ["s0", "s1", "s2", "s3"]


def _fresh_client(strategy: str, tmp_root: Path):
    dbfile = tmp_root / f"{strategy}.db"
    os.environ["REVIEWGATE_DB"] = str(dbfile)
    os.environ["REVIEWGATE_MODE"] = "A"
    from fastapi.testclient import TestClient

    import core.db as core_db
    core_db.DB_PATH = dbfile  # bind BEFORE any app import so lifespan seeds this file
    from straights import s0, s1, s2, s3  # noqa: F401 — import order fixes package path
    from importlib import import_module
    app = import_module(f"straights.{strategy}.app").app
    client = TestClient(app)

    # All four apps share the core.db.MODULE-global DB_PATH, which is read at
    # connection time. Re-bind it to this strategy's own file before every
    # request so the strategies' DBs stay isolated in one process.
    class _Isolated:
        def __getattr__(self, name):
            return getattr(client, name)

        def __enter__(self):
            self._bind()
            client.__enter__()
            return self

        def __exit__(self, *exc): return client.__exit__(*exc)

        def _bind(self):
            core_db.DB_PATH = dbfile
            os.environ["REVIEWGATE_DB"] = str(dbfile)

        def _req(self, method, path, **kw):
            self._bind()
            return getattr(client, method)(path, **kw)

        def get(self, *a, **kw):    return self._req("get", *a, **kw)
        def post(self, *a, **kw):   return self._req("post", *a, **kw)
        def put(self, *a, **kw):    return self._req("put", *a, **kw)
        def patch(self, *a, **kw):  return self._req("patch", *a, **kw)
        def delete(self, *a, **kw): return self._req("delete", *a, **kw)
    return _Isolated()


@pytest.fixture(scope="module")
def s0_client(tmp_path_factory):
    with _fresh_client("s0", tmp_path_factory.mktemp("rg-s0")) as c:
        yield c


@pytest.fixture(scope="module")
def s1_client(tmp_path_factory):
    with _fresh_client("s1", tmp_path_factory.mktemp("rg-s1")) as c:
        yield c


@pytest.fixture(scope="module")
def s2_client(tmp_path_factory):
    with _fresh_client("s2", tmp_path_factory.mktemp("rg-s2")) as c:
        yield c


@pytest.fixture(scope="module")
def s3_client(tmp_path_factory):
    with _fresh_client("s3", tmp_path_factory.mktemp("rg-s3")) as c:
        yield c