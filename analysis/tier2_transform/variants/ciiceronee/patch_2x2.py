"""ciiceronee 2x2 mechanism experiment: build arms from master (S2 base).

Modes:
  async-inline   async getter, called inline in the handler body
  async-depends  async getter, resolved via Depends()
  wrapper        sync getter called through anyio.to_thread.run_sync
  limiter-N      sync-depends (master) with anyio thread limiter set to N

Usage: MODE=<mode> <python> <this> <repo>
  For limiter modes, set MODE=limiter and LIMIT=<N>.
"""
import os
import sys

MODE = os.environ.get("MODE", "async-inline")
LIMIT = os.environ.get("LIMIT", "200")
REPO = sys.argv[1]
MAIN = os.path.join(REPO, "ciicerone/api/main.py")

# S2 style (global singleton, from master branch)
SYNC_GETTER_S2 = '''def get_simulator() -> Simulator:
    """Get the threat simulator instance."""
    if simulator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threat simulator not initialized"
        )
    return simulator


def get_llm_manager() -> LLMManager:
    """Get the LLM manager instance."""
    if llm_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM manager not initialized"
        )
    return llm_manager'''

ASYNC_GETTER_S2 = '''async def get_simulator() -> Simulator:
    """Get the threat simulator instance (async)."""
    if simulator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threat simulator not initialized"
        )
    return simulator


async def get_llm_manager() -> LLMManager:
    """Get the LLM manager instance (async)."""
    if llm_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM manager not initialized"
        )
    return llm_manager'''

# S4 style (container, from arm_s4 branch)
SYNC_GETTER_S4 = '''def get_simulator() -> Simulator:
    """Get the threat simulator instance from the container."""
    value = _CONTAINER.simulator()
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threat simulator not initialized"
        )
    return value


def get_llm_manager() -> LLMManager:
    """Get the LLM manager instance from the container."""
    value = _CONTAINER.llm_manager()
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM manager not initialized"
        )
    return value'''

ASYNC_GETTER_S4 = '''async def get_simulator() -> Simulator:
    """Get the threat simulator instance from the container (async)."""
    value = _CONTAINER.simulator()
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threat simulator not initialized"
        )
    return value


async def get_llm_manager() -> LLMManager:
    """Get the LLM manager instance from the container (async)."""
    value = _CONTAINER.llm_manager()
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM manager not initialized"
        )
    return value'''

def _detect_getter_style(src):
    if "value = _CONTAINER.simulator()" in src:
        return "s4"
    if "if simulator is None:" in src:
        return "s2"
    return None

SYNC_GETTER = None  # resolved at runtime
ASYNC_GETTER = None

INLINE_OLD = '''@app.get("/simulations/active")
async def get_active_simulations(sim: Simulator = Depends(get_simulator)):
    """Get currently active simulations."""
    try:
        active = sim.get_active_simulations()'''

INLINE_SYNC = '''@app.get("/simulations/active")
async def get_active_simulations():
    """Get currently active simulations."""
    sim = get_simulator()
    try:
        active = sim.get_active_simulations()'''

INLINE_ASYNC = '''@app.get("/simulations/active")
async def get_active_simulations():
    """Get currently active simulations."""
    sim = await get_simulator()
    try:
        active = sim.get_active_simulations()'''

INLINE_WRAPPER = '''@app.get("/simulations/active")
async def get_active_simulations():
    """Get currently active simulations."""
    import anyio
    sim = await anyio.to_thread.run_sync(get_simulator)
    try:
        active = sim.get_active_simulations()'''

DEP_ASYNC = '''@app.get("/simulations/active")
async def get_active_simulations(sim: Simulator = Depends(get_simulator)):
    """Get currently active simulations."""'''  # getter already async; signature unchanged


def main():
    src = open(MAIN).read()

    # Detect getter style (S2 = global singleton, S4 = container)
    style = _detect_getter_style(src)
    if style is None:
        raise SystemExit("ERROR: could not detect getter style (expected S2 global or S4 container). "
                         "Make sure you are on the master (S2) branch, not an already-patched branch.")
    sync_getter = SYNC_GETTER_S2 if style == "s2" else SYNC_GETTER_S4
    async_getter = ASYNC_GETTER_S2 if style == "s2" else ASYNC_GETTER_S4
    print(f"detected getter style: {style}")

    if MODE == "async-inline":
        if sync_getter not in src:
            if async_getter in src:
                print("getter already async, skipping getter replacement")
            else:
                raise SystemExit("ERROR: sync getter block missing and not already async.")
        else:
            src = src.replace(sync_getter, async_getter)
        assert INLINE_OLD in src, "inline signature missing"
        src = src.replace(INLINE_OLD, INLINE_ASYNC)

    elif MODE == "async-depends":
        if sync_getter not in src:
            if async_getter in src:
                print("getter already async, skipping getter replacement")
            else:
                raise SystemExit("ERROR: sync getter block missing and not already async.")
        else:
            src = src.replace(sync_getter, async_getter)
        # signature stays the same (Depends(get_simulator)), getter is now async
        # FastAPI will await it automatically

    elif MODE == "wrapper":
        assert INLINE_OLD in src, "inline signature missing"
        src = src.replace(INLINE_OLD, INLINE_WRAPPER)
        # ensure anyio is imported
        if "import anyio" not in src and "import anyio.to_thread" not in src:
            src = src.replace("from contextlib import asynccontextmanager",
                              "from contextlib import asynccontextmanager\nimport anyio.to_thread")

    elif MODE.startswith("limiter"):
        if style != "s2":
            raise SystemExit("ERROR: limiter mode requires S2 (master) branch.")
        # sync-depends (master) + add threadpool limiter to lifespan
        needle = "    yield\n\n    # Shutdown"
        assert needle in src, "lifespan yield not found"
        limiter_line = f"    anyio.to_thread.current_default_thread_limiter().total_tokens = {LIMIT}\n"
        # add import if missing
        if "import anyio.to_thread" not in src:
            src = src.replace("from contextlib import asynccontextmanager",
                              "from contextlib import asynccontextmanager\nimport anyio.to_thread")
        # insert limiter setting before yield (after startup, before yield)
        src = src.replace("    yield\n\n    # Shutdown",
                          "    anyio.to_thread.current_default_thread_limiter().total_tokens = int(os.environ.get('THREAD_LIMIT', '" + LIMIT + "'))\n    yield\n\n    # Shutdown")
        # ensure os imported
        if "import os" not in src:
            src = src.replace("import logging", "import logging\nimport os")

    else:
        raise SystemExit(f"MODE must be async-inline|async-depends|wrapper|limiter, got {MODE}")

    open(MAIN, "w").write(src)
    print(f"{MODE} (limit={LIMIT}) patched {MAIN}")


if __name__ == "__main__":
    main()