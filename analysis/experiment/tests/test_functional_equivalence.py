"""Functional-equivalence suite: all four strategy renders must behave identically.

S0 is the oracle. Two layers:

1. Read-only equality: for every idempotent probe (method, path, headers) the
   status code + JSON body produced by s1/s2/s3 must match s0 exactly, on
   isolated per-strategy DBs. No probe below mutates state, so module-scoped
   clients are safe to share.

2. Stateful write parity: identical write sequences applied to *fresh, isolated*
   per-strategy DBs must produce identical results and identical follow-up
   reads. Uses function-scoped clients so writes cannot leak across probes.

Plus a pinned auth matrix on the oracle.
"""

from __future__ import annotations

import pytest

from conftest import _fresh_client, STRATEGIES

ADMIN = {"Authorization": "Bearer admin-token"}
EDITOR = {"Authorization": "Bearer editor-token"}
USER = {"Authorization": "Bearer user-token"}
NONE = {}
BAD = {"Authorization": "Bearer definitely-not-a-token"}

# read-only / validation probes (no writes) — safe to run on module-scoped clients
PROBES = [
    ("get", "/reviews?limit=5&offset=0", NONE),
    ("get", "/reviews?limit=2&offset=20", NONE),
    ("get", "/reviews/search?q=Review&limit=10", NONE),
    ("get", "/reviews/search?q=zxqmv&limit=3", NONE),
    ("get", "/reviews/stats", NONE),
    ("get", "/reviews/1", NONE),
    ("get", "/reviews/1/comments", NONE),
    ("get", "/reviews/39/comments", NONE),
    ("get", "/reviews/99999", NONE),   # 404
    ("get", "/users/me", NONE),        # 401
    ("get", "/users/me", BAD),         # 401
    ("get", "/users/me", USER),
    ("get", "/users/me", EDITOR),
    ("get", "/users/me", ADMIN),
    ("get", "/users/admins", USER),
    ("post", "/reviews/1/votes", USER),             # missing body -> 422
    ("post", "/reviews/1/votes?value=-1", USER),    # 422: no body
    ("get", "/reviews/99999", EDITOR),              # 404
    ("post", "/reviews/1/approve", USER),           # 403 (no write occurs)
    ("get", "/reviews/export", ADMIN),
    ("get", "/reviews/export", USER),               # 403
    ("get", "/admin/dashboard", ADMIN),
    ("get", "/admin/config", ADMIN),
    ("get", "/admin/config", BAD),                  # 401
    ("post", "/admin/backup", ADMIN),               # no-op success
    ("get", "/users/dave/audit", ADMIN),
    ("get", "/users/dave/audit", NONE),             # 401
    ("get", "/users/nobody/audit", ADMIN),          # 404
]


def _body(client, probe):
    method, path, headers = probe
    r = getattr(client, method)(path, headers=headers)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


@pytest.mark.parametrize("probe", PROBES, ids=lambda p: f"{p[0]} {p[1]} {tuple(p[2])}")
def test_s1_equals_s0(probe, s0_client, s1_client):
    assert _body(s1_client, probe) == _body(s0_client, probe)


@pytest.mark.parametrize("probe", PROBES, ids=lambda p: f"{p[0]} {p[1]} {tuple(p[2])}")
def test_s2_equals_s0(probe, s0_client, s2_client):
    assert _body(s2_client, probe) == _body(s0_client, probe)


@pytest.mark.parametrize("probe", PROBES, ids=lambda p: f"{p[0]} {p[1]} {tuple(p[2])}")
def test_s3_equals_s0(probe, s0_client, s3_client):
    assert _body(s3_client, probe) == _body(s0_client, probe)


def test_auth_matrix_pinned(s0_client):
    assert s0_client.get("/users/me").status_code == 401
    assert s0_client.get("/users/me", headers=BAD).status_code == 401
    assert s0_client.get("/users/me", headers=USER).status_code == 200
    assert s0_client.get("/users/me", headers=EDITOR).status_code == 200
    assert s0_client.get("/users/me", headers=ADMIN).status_code == 200
    assert s0_client.get("/admin/dashboard", headers=USER).status_code == 403
    assert s0_client.get("/admin/dashboard", headers=EDITOR).status_code == 403
    assert s0_client.get("/admin/dashboard", headers=ADMIN).status_code == 200
    assert s0_client.get("/reviews/1").status_code == 200
    assert s0_client.get("/reviews/999999").status_code == 404


@pytest.mark.parametrize("strategy", [s for s in STRATEGIES if s != "s0"])
def test_stateful_write_parity(strategy, tmp_path):
    """Same write sequence on fresh isolated DBs must behave identically."""
    other = _fresh_client(strategy, tmp_path)
    oracle = _fresh_client("s0", tmp_path)

    def run(prefix, client):
        out = []
        out.append(("flag", client.post("/reviews/1/flag", headers=EDITOR)))
        out.append(("read1", client.get("/reviews/1", headers=NONE)))
        out.append(("del", client.delete("/reviews/5", headers=EDITOR)))
        out.append(("vote", client.post("/reviews/2/votes?value=1", headers=USER)))
        out.append(("suspend", client.post("/users/dave/suspend", headers=ADMIN)))
        out.append(("audit", client.get("/users/dave/audit", headers=ADMIN)))
        out.append(("create", client.post("/reviews", json={"title": "T", "body": "B", "rating": 4}, headers=EDITOR)))
        out.append(("stats", client.get("/reviews/stats", headers=NONE)))
        return [(k, r.status_code, r.json()) for k, r in out]

    with other, oracle:
        mine = run(strategy, other)
        expect = run("s0", oracle)
    for (mk, ms, mb), (ek, es, eb) in zip(mine, expect):
        assert (ms, mb) == (es, eb), f"{mk}: strategy {strategy} {ms}/{mb} != s0 {es}/{eb}"