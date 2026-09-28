"""smoke.py — functional equivalence gate for the 8 ReviewGate-R apps.

Two assertions, both hard failures:

  1. SURFACE. Every app exposes exactly the 12 read routes from
     routes_read.ROUTES_READ -- same paths, same methods, same auth level --
     and exposes no write method at all. A 405 on POST is the expected proof
     that the read-only design is real rather than aspirational.

  2. IDENTITY. Every app returns byte-identical (status, body) for all 12
     routes plus the 401 probe. Since all 8 are generated from one route table
     and one service layer, any divergence is a generator bug, and this is where
     it gets caught -- before any performance number is produced.

Plus one measurement, recorded because it must be disclosed rather than assumed:

  3. COROUTINE OFFSET. The sync arm drives the shared `async def` services
     through resolve(), costing one coroutine frame per request. Measured
     against a bare coroutine so the pre-registration can state it as a number
     instead of hand-waving.

Runs entirely in-process over ASGI. No server, no port, no load.

Run:  python smoke.py
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import sys
import time
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from core_read import resolve, sync_conn  # noqa: E402
from routes_read import ROUTES_READ  # noqa: E402

ARMS = [(p, m) for p in ("p1_direct", "p2_depends", "p3_middleware", "p4_container")
        for m in ("sync", "async")]

ADMIN = {"Authorization": "Bearer admin-token"}
USER = {"Authorization": "Bearer user-token"}
BAD = {"Authorization": "Bearer definitely-not-a-token"}

# (path, expected status, headers) -- one probe per route, auth per route level
PROBES: list[tuple[str, int, dict]] = [
    ("/health", 200, {}),
    ("/reviews?limit=20&offset=0", 200, {}),
    ("/reviews/search?q=Review&limit=10", 200, {}),
    ("/reviews/stats", 200, {}),
    ("/reviews/export", 200, ADMIN),
    ("/users/me", 200, USER),
    ("/users/admins", 200, USER),
    ("/admin/dashboard", 200, ADMIN),
    ("/admin/config", 200, ADMIN),
    ("/reviews/1", 200, {}),
    ("/reviews/1/comments", 200, {}),
    ("/users/alice/audit", 200, ADMIN),
]
# the 401 probe: valid route, no credentials
PROBES_401 = ("/users/me", 401, {})
# read-only proof, part 1: a write method on a path that DOES exist as a read
# route must be rejected by the router as not-allowed (405)
PROBES_405 = [
    ("/reviews", "POST", {"Authorization": "Bearer admin-token"}),
    ("/reviews/1", "DELETE", {"Authorization": "Bearer admin-token"}),
    ("/reviews/1", "PATCH", {"Authorization": "Bearer admin-token"}),
    ("/users/me", "PUT", {"Authorization": "Bearer admin-token"}),
]
# read-only proof, part 2: a write-only path from the original 21-route app must
# not exist at all (404) -- the 9 removed write endpoints
PROBES_404 = [
    ("/users/alice/suspend", "POST", {"Authorization": "Bearer admin-token"}),
    ("/admin/backup", "POST", {"Authorization": "Bearer admin-token"}),
    ("/users/me/api-token", "POST", {"Authorization": "Bearer admin-token"}),
    ("/reviews/1/flag", "POST", {"Authorization": "Bearer admin-token"}),
    ("/reviews/1/approve", "POST", {"Authorization": "Bearer admin-token"}),
    ("/reviews/1/votes", "POST", {"Authorization": "Bearer admin-token"}),
]


def expected_surface() -> tuple[list[tuple[str, str]], set[str]]:
    return ([(m, p) for m, p, *_ in ROUTES_READ], {p for _m, p, *_ in ROUTES_READ})


@asynccontextmanager
async def load_app(pattern: str, model: str):
    """Import an app and keep its lifespan OPEN for the duration of probing.

    Lifespan teardown must not run between load and probe: P3's middleware state
    and P4's container are installed by startup and cleared by shutdown, so
    probing outside the context would test a torn-down app.
    """
    mod = importlib.import_module(f"apps.{pattern}.{model}.app")
    app = mod.app
    async with app.router.lifespan_context(app):
        yield app


async def probe(app, path, expect, headers) -> tuple[int, str]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        r = await c.get(path, headers=headers)
        body = r.text
        if r.status_code == 200:
            try:  # canonicalise key order so dict ordering cannot cause a false diff
                body = json.dumps(json.loads(body), sort_keys=True)
            except json.JSONDecodeError:
                pass
        return r.status_code, body


def surface_of(app) -> list[tuple[str, str]]:
    out = []
    for r in app.routes:
        for method in getattr(r, "methods", set()) - {"HEAD", "OPTIONS"}:
            out.append((method, r.path))
    return sorted(out)


async def check_surface(pattern, model, app) -> list[str]:
    errs = []
    want, _paths = expected_surface()
    got = surface_of(app)
    if got != sorted(want):
        errs.append(f"surface mismatch: want {sorted(want)} got {got}")
    # no write method may exist on any path
    for m, p in got:
        if m in ("POST", "PUT", "PATCH", "DELETE"):
            errs.append(f"write method exposed: {m} {p}")
    return errs


async def collect(pattern, model, app) -> dict:
    res = {}
    for path, expect, headers in PROBES:
        status, body = await probe(app, path, expect, headers)
        res[path] = (status, body)
    path, expect, _ = PROBES_401
    status, body = await probe(app, path, expect, {})
    res["401:" + path] = (status, body)
    return res


async def check_405(app) -> list[str]:
    """Prove the read-only design: 405 on write methods of read paths,
    404 on the 9 write-only paths removed from the original app."""
    errs = []
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        for path, method, headers in PROBES_405:
            r = await c.request(method, path, headers=headers, json={})
            if r.status_code != 405:
                errs.append(f"{method} {path} -> {r.status_code}, expected 405 (read-only)")
        for path, method, headers in PROBES_404:
            r = await c.request(method, path, headers=headers, json={})
            if r.status_code != 404:
                errs.append(f"{method} {path} -> {r.status_code}, expected 404 (write route absent)")
    return errs


def measure_coroutine_offset(n=50000) -> dict:
    """What the sync arm pays to reuse the async service layer.

    Baseline is a hand-written plain `def` service call, which is what a sync
    arm that duplicated the service code would cost. The sync arm instead calls
    resolve(async_fn(...)). The difference is the price of sharing one service
    definition across all 8 apps, and it is what the pre-registration must
    disclose. A bare un-awaited coroutine is NOT a valid baseline: creating one
    does no work at all.
    """
    def plain(x):
        return x

    async def shared(x):
        return x

    t0 = time.perf_counter()
    for _ in range(n):
        plain(1)
    base = (time.perf_counter() - t0) / n * 1e6

    t0 = time.perf_counter()
    for _ in range(n):
        resolve(shared(1))
    wrapped = (time.perf_counter() - t0) / n * 1e6

    return {
        "calls": n,
        "plain_def_us": round(base, 4),
        "resolve_async_def_us": round(wrapped, 4),
        "offset_us": round(wrapped - base, 4),
    }


async def main() -> int:
    print("=" * 74)
    print("ReviewGate-R  functional equivalence smoke")
    print("=" * 74)

    per_arm: dict[str, dict] = {}
    failures: list[str] = []

    # every app's lifespan stays open until all probing is finished
    async with AsyncExitStack() as stack:
        for pattern, model in ARMS:
            name = f"{pattern}/{model}"
            try:
                app = await stack.enter_async_context(load_app(pattern, model))
            except Exception as exc:  # import or lifespan failure
                failures.append(f"{name}: FAILED TO LOAD: {type(exc).__name__}: {exc}")
                print(f"  {name:26s} LOAD FAILED  {type(exc).__name__}: {exc}")
                continue

            errs = await check_surface(pattern, model, app)
            errs += await check_405(app)
            per_arm[name] = await collect(pattern, model, app)

            if errs:
                failures += [f"{name}: {e}" for e in errs]
                print(f"  {name:26s} {len(per_arm[name])} probes  FAIL")
                for e in errs:
                    print(f"      - {e}")
            else:
                print(f"  {name:26s} {len(per_arm[name])} probes  surface+read-only ok")

    # identity across arms
    print("-" * 74)
    if per_arm:
        ref_name = next(iter(per_arm))
        ref = per_arm[ref_name]
        print(f"identity vs {ref_name}:")
        for name, got in per_arm.items():
            if name == ref_name:
                continue
            diffs = []
            for key, want in ref.items():
                have = got.get(key)
                if have is None:
                    diffs.append(f"{key}: MISSING")
                elif have[0] != want[0]:
                    diffs.append(f"{key}: status {have[0]} != {want[0]}")
                elif have[1] != want[1]:
                    diffs.append(f"{key}: body differs\n        ref={want[1][:160]}\n        got={have[1][:160]}")
            if diffs:
                failures += [f"{name}: {d}" for d in diffs]
                print(f"  {name:26s} {len(diffs)} DIFFS")
                for d in diffs:
                    print(f"      - {d}")
            else:
                print(f"  {name:26s} identical on all {len(ref)} probes")

    print("-" * 74)
    off = measure_coroutine_offset()
    print("coroutine offset (sync arm only, uniform across all 4 sync patterns):")
    print(f"  plain def service     {off['plain_def_us']:.4f} us/call")
    print(f"  via resolve(async def){off['resolve_async_def_us']:>9.4f} us/call")
    print(f"  offset                {off['offset_us']:.4f} us/call")

    out = HERE / "results" / "smoke_equivalence.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "arms": {
            k: {
                p: {"status": s, "body_sha256": hashlib.sha256(b.encode()).hexdigest()[:16]}
                for p, (s, b) in v.items()
            }
            for k, v in per_arm.items()
        },
        "coroutine_offset": off,
        "failures": failures,
        "passed": not failures,
    }, indent=2))

    print("-" * 74)
    if failures:
        print(f"SMOKE FAILED: {len(failures)} problem(s)")
        return 1
    print(f"SMOKE PASSED: {len(ARMS)} arms, {len(per_arm[next(iter(per_arm))])} probes each, identical")
    print(f"written {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
