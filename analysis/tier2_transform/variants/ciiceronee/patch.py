"""ciiceronee: swap the DI pattern in ciicerone/api/main.py.

Modes:
  s1  handlers drop the Depends param and call get_simulator()/get_llm_manager()
      explicitly (no framework DI anywhere in main.py).
  s3  middleware resolves the singletons once and stashes them on request.state;
      handlers read the ambient state via `req: Request`.
  s4  dependency-injector container owns the singletons; getters read the
      container; lifespan overrides the providers with the real instances.

Usage: MODE=s1|s3|s4 <toolenv>/bin/python <this> <repo>
"""

import os
import sys

MODE = os.environ.get("MODE", "s1")
REPO = sys.argv[1]
MAIN = os.path.join(REPO, "ciicerone/api/main.py")

# (handler, var, type, getter, body_uses_request_name, state_key)
HANDLERS = [
    ("run_simulation", "sim", "Simulator", "get_simulator", "request: SimulationRequest", "simulator"),
    ("get_active_simulations", "sim", "Simulator", "get_simulator", None, "simulator"),
    ("generate_content", "llm", "LLMManager", "get_llm_manager", "request: ContentGenerationRequest", "llm_manager"),
    ("list_providers", "llm", "LLMManager", "get_llm_manager", None, "llm_manager"),
    ("llm_status", "llm", "LLMManager", "get_llm_manager", None, "llm_manager"),
]

INLINE = {
    "get_active_simulations": "async def get_active_simulations(sim: Simulator = Depends(get_simulator)):",
    "list_providers": "async def list_providers(llm: LLMManager = Depends(get_llm_manager)):",
    "llm_status": "async def llm_status(llm: LLMManager = Depends(get_llm_manager)):",
}

MULTI = {
    "run_simulation": ("async def run_simulation(\n    request: SimulationRequest,\n    sim: Simulator = Depends(get_simulator)\n):", "async def run_simulation(\n    request: SimulationRequest\n):"),
    "generate_content": ("async def generate_content(\n    request: ContentGenerationRequest,\n    llm: LLMManager = Depends(get_llm_manager)\n):", "async def generate_content(\n    request: ContentGenerationRequest\n):"),
}


def insert_prologue(src: str, handler_anchor: str, stmt: str, indent: int = 4) -> str:
    """Insert `stmt` at the top of the handler body, after any docstring."""
    needle = f"async def {handler_anchor}("
    idx = src.index(needle) + len(needle)
    depth = 1
    j = idx
    while depth:
        if src[j] == "(":
            depth += 1
        elif src[j] == ")":
            depth -= 1
        j += 1
    # now src[j-1] is the ')' that closes the signature; expect ':' next
    assert src[j] == ":", f"{handler_anchor}: expected ':' after signature"
    body_start = j + 2  # skip ':\n'
    line_end = src.index("\n", body_start)
    first = src[body_start:line_end]
    if '"""' in first:
        insert_at = line_end + 1
    else:
        insert_at = body_start
    pad = " " * indent
    return src[:insert_at] + pad + stmt + "\n" + src[insert_at:]


def patch_s1(src: str) -> str:
    for name, var, typ, getter, _, _ in HANDLERS:
        if name in MULTI:
            old, new = MULTI[name]
            assert old in src, f"{name}: multi signature missing"
            src = src.replace(old, new)
        else:
            old = INLINE[name]
            assert old in src, f"{name}: inline signature missing"
            nv = old.replace(f"{var}: {typ} = Depends({getter})", "")
            src = src.replace(old, nv)
        src = insert_prologue(src, name, f"{var} = {getter}()")
    src = src.replace("from fastapi import FastAPI, HTTPException, Depends, status",
                      "from fastapi import FastAPI, HTTPException, status")
    return src


def patch_s3(src: str) -> str:
    # replace each Depends param with an explicit `req: Request` ambient read
    for name, var, typ, getter, bodyreq, state_key in HANDLERS:
        if bodyreq:
            old, new = MULTI[name]
            # keep the body param, add req: Request, drop the Depends param
            new = new.replace("\n):", f",\n    req: Request\n):")
            assert old in src
            src = src.replace(old, new)
        else:
            old = INLINE[name]
            nv = old.replace(f"{var}: {typ} = Depends({getter})", "req: Request")
            assert old in src
            src = src.replace(old, nv)
        src = insert_prologue(src, name, f"{var} = req.state.{state_key}")
    return src


MIDDLEWARE = '''
@app.middleware("http")
async def ambient_context(request: Request, call_next):
    """S3: resolve the app singletons once and expose them on request.state."""
    try:
        request.state.simulator = get_simulator()
        request.state.llm_manager = get_llm_manager()
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)

'''


def patch_s4(src: str) -> str:
    old_getters = '''def get_simulator() -> Simulator:
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
    new_getters = '''class CiiceroneContainer(containers.DeclarativeContainer):
    """dependency-injector container owning the singletons (S4)."""

    simulator = providers.Object()
    llm_manager = providers.Object()


def get_simulator() -> Simulator:
    """Get the threat simulator instance from the container."""
    value = CiiceroneContainer().simulator()
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Threat simulator not initialized"
        )
    return value


def get_llm_manager() -> LLMManager:
    """Get the LLM manager instance from the container."""
    value = CiiceroneContainer().llm_manager()
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM manager not initialized"
        )
    return value'''
    assert old_getters in src
    src = src.replace(old_getters, new_getters)

    old = "from ciicerone.llm.manager import LLMManager"
    assert old in src
    src = src.replace(old, old + "\n\nfrom dependency_injector import containers, providers")

    old_start = "        llm_manager = LLMManager()\n        simulator = Simulator(llm_provider=llm_manager)"
    new_start = ("        llm_manager = LLMManager()\n"
                 "        simulator = Simulator(llm_provider=llm_manager)\n"
                 "        CiiceroneContainer.simulator.override(providers.Object(simulator))\n"
                 "        CiiceroneContainer.llm_manager.override(providers.Object(llm_manager))")
    assert old_start in src
    src = src.replace(old_start, new_start)
    return src


def main() -> None:
    src = open(MAIN).read()
    if MODE == "s1":
        out = patch_s1(src)
    elif MODE == "s3":
        out = patch_s3(src)
        # register middleware right after app creation
        needle = '    lifespan=lifespan\n)'
        assert needle in out
        block_end = out.index(needle) + len(needle)
        out = out[:block_end] + "\n\n" + MIDDLEWARE + out[block_end:]
        # ensure Request + JSONResponse imports, drop Depends
        out = out.replace("from fastapi import FastAPI, HTTPException, Depends, status",
                          "from fastapi import FastAPI, HTTPException, Request, status")
        out = out.replace("from fastapi.responses import JSONResponse\n\n# Create FastAPI app",
                          "from fastapi.responses import JSONResponse\n\n# Create FastAPI app")
        if "from fastapi.responses import JSONResponse" not in out:
            out = out.replace("from fastapi import FastAPI, HTTPException, Request, status",
                              "from fastapi import FastAPI, HTTPException, Request, status\nfrom fastapi.responses import JSONResponse")
    elif MODE == "s4":
        out = patch_s4(src)
        # add dependency-injector to runtime requirements
        req = os.path.join(REPO, "requirements.txt")
        txt = open(req).read()
        if "dependency-injector" not in txt:
            txt = txt + "\ndependency-injector>=4.41.0\n"
            open(req, "w").write(txt)
    else:
        raise SystemExit("MODE must be s1|s3|s4")

    open(MAIN, "w").write(out)
    print(f"{MODE} patched {MAIN}")


if __name__ == "__main__":
    main()