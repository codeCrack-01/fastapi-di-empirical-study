import anyio.to_thread
import threading
import core_read
from apps.p2_depends.sync.app import app


@app.get("/__diag")
def __diag():
    """Diagnostic only - NOT part of the measured app. Reports the live
    threadlimiter tokens and how many sync-pool connections are free."""
    tl = anyio.to_thread.current_default_thread_limiter()
    q = core_read._get_sync_pool()
    return {
        "total_tokens": tl.total_tokens,
        "borrowed_tokens": getattr(tl, "borrowed_tokens", None),
        "pool_free": q.qsize(),
        "os_threads": threading.active_count(),
    }
